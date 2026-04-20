"""
backend/rag/predictor.py
Predict future disease risk and suggest precautions using Groq Llama 3.
Reads current health data (vitals, blood reports, history, medications, etc.)
from retrieved chunks and returns a structured risk-assessment JSON.
"""

from __future__ import annotations

import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHAT_MODEL   = os.getenv("CHAT_MODEL", "llama-3.3-70b-versatile")
MAX_TOKENS   = 2000          # slightly higher — precautions lists can be long


_groq_client: Groq | None = None


def _get_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment / .env file")
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


# ── System prompt ──────────────────────────────────────────────────────────────
PREDICTION_SYSTEM_PROMPT = """You are a clinical AI risk-assessment assistant. \
Given clinical document excerpts (which may include vitals, blood/lab reports, \
medication lists, past diagnoses, imaging findings, or doctor notes), your job is to:

1. Identify ALL health indicators present in the documents.
2. Based on those indicators, predict which diseases or conditions the patient is \
   at risk of developing in the future.
3. Estimate a probability (as a percentage) and time horizon for each predicted condition.
4. Suggest concrete, actionable precautions to reduce each risk.
5. Recommend lifestyle changes (diet, exercise, sleep, stress management, habits).
6. List follow-up diagnostic tests or screenings the patient should consider.

Rules:
- Base every prediction strictly on evidence found in the provided document chunks.
- Cite the source chunk for every prediction using format [source: filename, chunk N].
- Never fabricate lab values, diagnoses, or medical facts not present in the documents.
- If a data type is missing (e.g. no blood report), say "Insufficient data" for that section.
- Use plain language for precautions — the patient may read this directly.
- Probability percentages are estimates based on clinical patterns, not guarantees.
- Always include a medical disclaimer in the "disclaimer" field.
- Return ONLY valid JSON — no markdown, no explanation outside the JSON.

Return your response as a JSON object with EXACTLY these keys:
{
  "risk_level": "low | moderate | high",
  "risk_summary": "2-3 sentence plain-language overview of the patient's overall risk profile",
  "predicted_conditions": [
    {
      "condition": "condition name",
      "probability": "estimated % chance if current trajectory continues",
      "time_horizon": "e.g. within 5 years / within 10 years",
      "supporting_evidence": "which indicators from the documents suggest this risk",
      "citation": "[source: filename, chunk N]"
    }
  ],
  "reasoning": "detailed clinical reasoning — what patterns in the data led to these predictions",
  "precautions": [
    "specific actionable step 1",
    "specific actionable step 2"
  ],
  "lifestyle_changes": {
    "diet": "dietary recommendations based on the patient's risk profile",
    "exercise": "exercise recommendations",
    "sleep": "sleep hygiene recommendations if relevant",
    "habits": "any substance use, smoking, alcohol guidance",
    "stress": "stress management recommendations if relevant"
  },
  "follow_up_tests": [
    {
      "test": "test name",
      "reason": "why this test is recommended",
      "frequency": "how often"
    }
  ],
  "data_gaps": "list any missing information that would improve prediction accuracy",
  "sources_used": ["filename1", "filename2"],
  "disclaimer": "This is an AI-generated predictive analysis for informational purposes only. It is not a medical diagnosis. Always consult a qualified physician or specialist before making any health decisions."
}"""


# ── Helpers ────────────────────────────────────────────────────────────────────

def _build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a numbered context block for the prompt."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "unknown")
        idx    = chunk.get("chunk_index", 0)
        text   = chunk.get("text", "").strip()
        parts.append(f"[Chunk {i} | source: {source} | chunk index: {idx}]\n{text}")
    return "\n\n---\n\n".join(parts)


def _empty_prediction(query: str, reason: str) -> dict:
    """Return a safe empty prediction when no chunks are available."""
    return {
        "risk_level":           "unknown",
        "risk_summary":         reason,
        "predicted_conditions": [],
        "reasoning":            reason,
        "precautions":          ["Please upload relevant clinical documents (blood reports, vitals, doctor notes) to enable prediction."],
        "lifestyle_changes": {
            "diet":     "Insufficient data",
            "exercise": "Insufficient data",
            "sleep":    "Insufficient data",
            "habits":   "Insufficient data",
            "stress":   "Insufficient data",
        },
        "follow_up_tests": [],
        "data_gaps":        "No clinical documents were retrieved.",
        "sources_used":     [],
        "disclaimer":       "This is an AI-generated predictive analysis for informational purposes only. It is not a medical diagnosis. Always consult a qualified physician or specialist before making any health decisions.",
        "query":            query,
        "model":            CHAT_MODEL,
        "num_chunks_used":  0,
    }


def _parse_response(raw: str) -> dict:
    """Strip markdown fences if present and parse JSON."""
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── Public API ─────────────────────────────────────────────────────────────────

def predict(query: str, chunks: list[dict]) -> dict:
    """
    Generate a structured disease-risk prediction and precaution plan.

    Parameters
    ----------
    query  : the user's health question or context
             e.g. "Based on my blood reports and vitals, what diseases am I at risk of?"
    chunks : retrieved chunks from ChromaDB (from retriever.py)

    Returns
    -------
    dict with keys:
        risk_level, risk_summary, predicted_conditions, reasoning,
        precautions, lifestyle_changes, follow_up_tests, data_gaps,
        sources_used, disclaimer, query, model, num_chunks_used
    """
    if not chunks:
        return _empty_prediction(
            query,
            "No clinical documents were retrieved. Please upload blood reports, "
            "vitals, or doctor notes to enable risk prediction.",
        )

    context      = _build_context(chunks)
    user_message = (
        f"Patient Health Query: {query}\n\n"
        f"Retrieved Clinical Document Excerpts:\n\n{context}\n\n"
        f"Based on all the above clinical data, provide a detailed disease risk "
        f"prediction with precautions and lifestyle recommendations."
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
            temperature = 0.15,   # slightly higher than summarizer for nuanced risk reasoning
        )
    except Exception as exc:
        raise RuntimeError(f"Groq API call failed: {exc}") from exc

    raw_content = response.choices[0].message.content.strip()

    try:
        prediction = _parse_response(raw_content)
    except json.JSONDecodeError:
        # Fallback: preserve raw output in risk_summary so nothing is lost
        prediction = {
            "risk_level":           "unknown",
            "risk_summary":         raw_content,
            "predicted_conditions": [],
            "reasoning":            "JSON parsing failed — raw model output stored in risk_summary.",
            "precautions":          [],
            "lifestyle_changes": {
                "diet": "", "exercise": "", "sleep": "", "habits": "", "stress": ""
            },
            "follow_up_tests": [],
            "data_gaps":        "JSON parsing error — please retry.",
            "sources_used":     [],
            "disclaimer":       "This is an AI-generated predictive analysis for informational purposes only. It is not a medical diagnosis. Always consult a qualified physician or specialist before making any health decisions.",
        }

    # Attach request metadata
    prediction["query"]           = query
    prediction["model"]           = CHAT_MODEL
    prediction["num_chunks_used"] = len(chunks)

    # Always enforce disclaimer (overwrite whatever the model returned)
    prediction["disclaimer"] = (
        "This is an AI-generated predictive analysis for informational purposes only. "
        "It is not a medical diagnosis. Always consult a qualified physician or specialist "
        "before making any health decisions."
    )

    return prediction


# ── Quick smoke-test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    dummy_chunks = [
        {
            "chunk_id":    "test_chunk_0000",
            "text":        (
                "Patient: Male, 52 years. BP: 148/94 mmHg (elevated). "
                "FBS: 118 mg/dL (impaired fasting glucose). "
                "HbA1c: 6.2% (prediabetic range). "
                "BMI: 28.4 (overweight). "
                "LDL: 142 mg/dL (borderline high). HDL: 38 mg/dL (low). "
                "Triglycerides: 210 mg/dL (high). "
                "Family history: Father had Type 2 DM, Mother had hypertension."
            ),
            "source":      "patient_labs_2024.txt",
            "chunk_index": 0,
        },
        {
            "chunk_id":    "test_chunk_0001",
            "text":        (
                "Lifestyle: Sedentary desk job, no regular exercise. "
                "Smokes 5 cigarettes/day for 10 years. "
                "Alcohol: 2-3 units/week. "
                "Diet: High in processed foods, low fibre intake. "
                "Sleep: 5-6 hours/night, reports fatigue. "
                "Stress: High work-related stress."
            ),
            "source":      "patient_labs_2024.txt",
            "chunk_index": 1,
        },
    ]

    result = predict(
        "Based on my blood reports and lifestyle, what diseases am I at risk of developing?",
        dummy_chunks,
    )

    print("\n── Prediction Output ───────────────────────────────")
    print(f"Risk Level : {result.get('risk_level')}")
    print(f"Summary    : {result.get('risk_summary')}")
    print(f"\nPredicted conditions:")
    for cond in result.get("predicted_conditions", []):
        print(f"  • {cond.get('condition')} — {cond.get('probability')} ({cond.get('time_horizon')})")
    print(f"\nPrecautions ({len(result.get('precautions', []))}):")
    for p in result.get("precautions", [])[:3]:
        print(f"  - {p}")
    print(f"\nDisclaimer : {result.get('disclaimer')}")