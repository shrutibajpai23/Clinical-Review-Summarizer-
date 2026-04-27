"""
backend/rag/predictor.py

Timeline-aware disease risk prediction using Groq Llama 3.3.

Key upgrade: every predicted condition is anchored to real dates
extracted from the clinical document. Instead of vague "within 5 years",
the model produces specific date ranges calculated from documented events:
  - trigger_date   : the date from the document that grounds this prediction
  - onset_window   : expected start date range e.g. "May 3 – May 10, 2025"
  - peak_date      : when the condition is likely worst / most acute
  - resolution_date: expected recovery / stabilisation date (if applicable)
  - status         : active | developing | resolving | chronic | at_risk

All dates must be derivable from something explicitly in the document.
If no dates are present, fields are set to "Not documented" — never fabricated.
"""

from __future__ import annotations

import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHAT_MODEL   = os.getenv("CHAT_MODEL", "llama-3.3-70b-versatile")
MAX_TOKENS   = 2500

_groq_client: Groq | None = None

def _get_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment / .env file")
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


PREDICTION_SYSTEM_PROMPT = """You are a senior clinical AI analyst specialising in \
timeline-aware disease progression modelling.

Given clinical document excerpts, follow these steps exactly:

STEP 1 — DATE EXTRACTION
Scan every chunk carefully for ANY dates or time references:
- Explicit dates   : "April 25 2025", "25/04/25", "2025-04-25"
- Relative times   : "3 days ago", "admitted last Tuesday", "follow-up in 2 weeks"
- Duration markers : "symptoms for 6 days", "on medication since March"
- Event anchors    : "post-surgery Day 3", "discharged after 5-day stay"
Convert all relative references to approximate calendar dates where possible.
Collect ALL found dates into the "document_dates" array.

STEP 2 — GROUNDED PREDICTION
For every predicted condition:
- Identify the SPECIFIC clinical indicator that triggers this prediction
  (e.g. "HbA1c 6.2% recorded April 20" or "BP 148/94 on admission April 25")
- Use that indicator's date as the anchor for the timeline
- Calculate realistic date windows using established clinical knowledge:
    * Acute infections   : onset 1-3 days, peak 3-7 days, resolution 7-14 days
    * Post-op recovery   : weeks to months depending on procedure
    * Chronic conditions : months to years progression
    * Lab-driven risks   : use standard clinical progression timelines
- If NO date exists for the trigger, set all timeline fields to "Not documented"
  NEVER invent a date not derivable from the document

STEP 3 — STATUS CLASSIFICATION
Assign each condition one status:
- "active"     : currently present in the document
- "developing" : not yet present but progression indicators found
- "resolving"  : was present, now improving per document data
- "chronic"    : long-standing, unlikely to resolve
- "at_risk"    : patient has risk factors, no current indicators

STEP 4 — PRECAUTIONS AND LIFESTYLE
Ground every precaution to a specific finding in the document.
Be specific to this patient's data — no generic advice.

STRICT RULES:
- Every date range MUST be anchored to a real date from the document
- If no date found, write "Not documented" — never guess a date
- Never fabricate lab values, diagnoses, or clinical facts not in the document
- Cite the source chunk for every predicted condition
- Return ONLY valid JSON — no markdown, no text outside the JSON

Return EXACTLY this JSON structure (no extra keys, no missing keys):

{
  "document_dates": [
    {
      "raw_text": "exact text from document containing the date reference",
      "interpreted_date": "standardised date e.g. April 25, 2025",
      "event": "brief description of what happened on this date"
    }
  ],
  "reference_date": "the most recent or most clinically relevant date found. Write Not documented if none found.",
  "risk_level": "low | moderate | high",
  "risk_summary": "2-3 sentence plain-language overview anchored to the patient's documented timeline",
  "predicted_conditions": [
    {
      "condition": "full condition name",
      "status": "active | developing | resolving | chronic | at_risk",
      "probability": "e.g. 72% based on documented indicators",
      "trigger": "the specific clinical finding that grounds this prediction, with its date if available",
      "timeline": {
        "trigger_date": "date of the clinical indicator that grounds this prediction, or Not documented",
        "onset_window": "expected start date range e.g. April 28 to May 3 2025, or Not documented",
        "peak_date": "expected worst point e.g. around May 5 2025, or Not applicable, or Not documented",
        "resolution_date": "expected recovery e.g. May 14 to May 20 2025, or Ongoing chronic, or Not documented",
        "confidence": "high | medium | low",
        "basis": "clinical reasoning for these specific dates e.g. Typical UTI resolves in 7-10 days from symptom onset"
      },
      "supporting_evidence": "which specific values or findings from the document support this",
      "citation": "[source: filename, chunk N]"
    }
  ],
  "disease_progression_summary": "A plain-English paragraph describing the overall expected clinical trajectory for this patient with dates where available.",
  "reasoning": "detailed clinical reasoning linking document findings to predictions",
  "precautions": [
    "specific actionable precaution grounded to a finding in this document"
  ],
  "lifestyle_changes": {
    "diet":     "specific dietary recommendation based on this patient's documented data",
    "exercise": "specific exercise recommendation",
    "sleep":    "specific sleep recommendation",
    "habits":   "specific habits recommendation",
    "stress":   "specific stress management recommendation"
  },
  "follow_up_tests": [
    {
      "test": "test name",
      "reason": "why — linked to a specific finding in the document",
      "recommended_date": "when e.g. by May 10 2025 if reference date exists, else within 2 weeks of next visit",
      "frequency": "ongoing frequency after initial test"
    }
  ],
  "data_gaps": "specific missing information that would improve timeline accuracy",
  "sources_used": ["filename1"],
  "disclaimer": "This is an AI-generated predictive analysis for informational purposes only. It is not a medical diagnosis. Always consult a qualified physician or specialist before making any health decisions."
}"""


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "unknown")
        idx    = chunk.get("chunk_index", 0)
        text   = chunk.get("text", "").strip()
        parts.append(f"[Chunk {i} | source: {source} | chunk index: {idx}]\n{text}")
    return "\n\n---\n\n".join(parts)


def _empty_prediction(query: str, reason: str) -> dict:
    return {
        "document_dates":             [],
        "reference_date":             "Not documented",
        "risk_level":                 "unknown",
        "risk_summary":               reason,
        "predicted_conditions":       [],
        "disease_progression_summary": reason,
        "reasoning":                  reason,
        "precautions":                ["Please upload relevant clinical documents to enable prediction."],
        "lifestyle_changes": {
            "diet": "Insufficient data", "exercise": "Insufficient data",
            "sleep": "Insufficient data", "habits": "Insufficient data",
            "stress": "Insufficient data",
        },
        "follow_up_tests": [],
        "data_gaps":       "No clinical documents were retrieved.",
        "sources_used":    [],
        "disclaimer":      "This is an AI-generated predictive analysis for informational purposes only. "
                           "It is not a medical diagnosis. Always consult a qualified physician or specialist "
                           "before making any health decisions.",
        "query":           query,
        "model":           CHAT_MODEL,
        "num_chunks_used": 0,
    }


def _parse_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw   = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def predict(query: str, chunks: list[dict]) -> dict:
    """
    Generate a timeline-aware disease-risk prediction.

    Returns a dict with:
      document_dates, reference_date, risk_level, risk_summary,
      predicted_conditions (each with status + timeline: trigger_date,
      onset_window, peak_date, resolution_date, confidence, basis),
      disease_progression_summary, reasoning, precautions,
      lifestyle_changes, follow_up_tests (with recommended_date),
      data_gaps, sources_used, disclaimer.
    """
    if not chunks:
        return _empty_prediction(
            query,
            "No clinical documents were retrieved. Please upload blood reports, "
            "vitals, or doctor notes to enable prediction.",
        )

    context = _build_context(chunks)
    user_message = (
        f"Patient Health Query: {query}\n\n"
        f"IMPORTANT: Extract every date mentioned in the document. "
        f"Anchor every predicted condition timeline to a real date from the document. "
        f"If the document says 'April 25', use that as the event date and calculate "
        f"onset/peak/resolution windows from it using clinical progression knowledge.\n\n"
        f"Retrieved Clinical Document Excerpts:\n\n{context}\n\n"
        f"Step 1: Extract all dates from the document into document_dates.\n"
        f"Step 2: For each predicted condition anchor its timeline to a real document date.\n"
        f"Step 3: Generate precautions and follow-up tests with specific date recommendations.\n"
        f"Return the complete JSON."
    )

    client = _get_client()

    try:
        response = client.chat.completions.create(
            model       = CHAT_MODEL,
            max_tokens  = MAX_TOKENS,
            messages    = [
                {"role": "system", "content": PREDICTION_SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            temperature = 0.10,
        )
    except Exception as exc:
        raise RuntimeError(f"Groq API call failed: {exc}") from exc

    raw_content = response.choices[0].message.content.strip()

    try:
        prediction = _parse_response(raw_content)
    except json.JSONDecodeError:
        prediction = {
            "document_dates":             [],
            "reference_date":             "Not documented",
            "risk_level":                 "unknown",
            "risk_summary":               raw_content,
            "predicted_conditions":       [],
            "disease_progression_summary": "JSON parsing failed — raw output stored in risk_summary.",
            "reasoning":                  "JSON parsing failed.",
            "precautions":                [],
            "lifestyle_changes": {"diet": "", "exercise": "", "sleep": "", "habits": "", "stress": ""},
            "follow_up_tests":            [],
            "data_gaps":                  "JSON parsing error — please retry.",
            "sources_used":               [],
            "disclaimer":                 "",
        }

    prediction["query"]           = query
    prediction["model"]           = CHAT_MODEL
    prediction["num_chunks_used"] = len(chunks)

    # Always enforce disclaimer — model cannot override this
    prediction["disclaimer"] = (
        "This is an AI-generated predictive analysis for informational purposes only. "
        "It is not a medical diagnosis. Always consult a qualified physician or specialist "
        "before making any health decisions."
    )

    return prediction


if __name__ == "__main__":
    dummy_chunks = [
        {
            "chunk_id":    "test_chunk_0000",
            "text": (
                "Admission date: April 25, 2025. "
                "Patient: Female, 34 years. Chief complaint: burning urination, fever 38.9 C. "
                "Diagnosis: Acute Urinary Tract Infection (UTI). "
                "Urine culture: E. coli > 100,000 CFU/mL. WBC: 14,200 (elevated). CRP: 48 mg/L. "
                "Prescribed: Nitrofurantoin 100mg twice daily for 7 days. "
                "Follow-up scheduled: May 3, 2025."
            ),
            "source":      "patient_note_april2025.txt",
            "chunk_index": 0,
        },
        {
            "chunk_id":    "test_chunk_0001",
            "text": (
                "History: Recurrent UTIs — 2 episodes in past 6 months (November 2024, February 2025). "
                "BP: 122/78. BMI: 24.1. No diabetes. "
                "Doctor note: If symptoms do not resolve by May 3, consider imaging. "
                "Patient advised to return if fever persists beyond April 28."
            ),
            "source":      "patient_note_april2025.txt",
            "chunk_index": 1,
        },
    ]

    result = predict("What is the disease timeline and what risks should I watch for?", dummy_chunks)

    print(f"\nReference date : {result.get('reference_date')}")
    print(f"Risk level     : {result.get('risk_level')}")
    print(f"Dates found    : {len(result.get('document_dates', []))}")
    print(f"\nProgression:\n{result.get('disease_progression_summary','')[:300]}")
    for c in result.get("predicted_conditions", []):
        tl = c.get("timeline", {})
        print(f"\n  • {c.get('condition')} [{c.get('status')}]")
        print(f"    Trigger    : {tl.get('trigger_date')}")
        print(f"    Onset      : {tl.get('onset_window')}")
        print(f"    Peak       : {tl.get('peak_date')}")
        print(f"    Resolution : {tl.get('resolution_date')}")