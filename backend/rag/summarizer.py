"""
backend/rag/summarizer.py
Generate structured clinical summaries using Groq Llama 3.
Never hallucinate — cites source chunks for every claim.
"""

from __future__ import annotations

import os
import json
from dotenv import load_dotenv
from groq import Groq
from backend.rag.predictor import predict  

load_dotenv()

# ── Config 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHAT_MODEL   = os.getenv("CHAT_MODEL", "llama-3.3-70b-versatile")
MAX_TOKENS   = 1500


_groq_client: Groq | None = None


def _get_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment / .env file")
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


SYSTEM_PROMPT = """You are a clinical AI assistant. Given clinical document excerpts below, \
produce a structured medical summary with these exact sections:
- Patient/Study Overview
- Key Findings
- Diagnosis / Conclusions
- Recommendations / Next Steps
- Limitations or Risks

Rules:
1. Cite the source chunk for every claim using format [source: filename, chunk N]
2. Never hallucinate medical facts
3. If information is missing, say "Not mentioned in provided documents"
4. Be concise but complete
5. Use medical terminology appropriately
6. Return ONLY valid JSON — no markdown, no explanation outside the JSON

Return your response as a JSON object with exactly these keys:
{
  "overview": "...",
  "key_findings": "...",
  "diagnosis": "...",
  "recommendations": "...",
  "limitations": "...",
  "sources_used": ["filename1", "filename2"]
}"""


def _build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a numbered context block for the prompt."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "unknown")
        idx    = chunk.get("chunk_index", 0)
        text   = chunk.get("text", "").strip()
        parts.append(f"[Chunk {i} | source: {source} | chunk index: {idx}]\n{text}")
    return "\n\n---\n\n".join(parts)


def summarize(query: str, chunks: list[dict]) -> dict:
    """
    Generate a structured clinical summary for a query given retrieved chunks.

    Parameters
    ----------
    query  : the user's clinical question
    chunks : retrieved chunks from ChromaDB (from retriever.py)

    Returns
    -------
    dict with keys:
        overview, key_findings, diagnosis, recommendations,
        limitations, sources_used, query, model, num_chunks_used
    """
    if not chunks:
        return {
            "overview":        "Not mentioned in provided documents",
            "key_findings":    "Not mentioned in provided documents",
            "diagnosis":       "Not mentioned in provided documents",
            "recommendations": "Not mentioned in provided documents",
            "limitations":     "No source documents were retrieved.",
            "sources_used":    [],
            "query":           query,
            "model":           CHAT_MODEL,
            "num_chunks_used": 0,
        }

    context      = _build_context(chunks)
    user_message = (
        f"Clinical Question: {query}\n\n"
        f"Retrieved Document Excerpts:\n\n{context}"
    )

    client = _get_client()

    try:
        response = client.chat.completions.create(
            model      = CHAT_MODEL,
            max_tokens = MAX_TOKENS,
            messages   = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            temperature = 0.1,   # low temp for factual medical output
        )
    except Exception as exc:
        raise RuntimeError(f"Groq API call failed: {exc}") from exc

    raw_content = response.choices[0].message.content.strip()

    # ── Parse JSON response
    try:
        # Strip markdown fences if model adds them anyway
        if raw_content.startswith("```"):
            raw_content = raw_content.split("```")[1]
            if raw_content.startswith("json"):
                raw_content = raw_content[4:]
        summary = json.loads(raw_content.strip())
    except json.JSONDecodeError:
        # Fallback: wrap raw text in structured dict
        summary = {
            "overview":        raw_content,
            "key_findings":    "Not mentioned in provided documents",
            "diagnosis":       "Not mentioned in provided documents",
            "recommendations": "Not mentioned in provided documents",
            "limitations":     "JSON parsing failed — raw model output above",
            "sources_used":    [],
        }

    # ── Attach meta 
    summary["query"]           = query
    summary["model"]           = CHAT_MODEL
    summary["num_chunks_used"] = len(chunks)

    return summary



if __name__ == "__main__":
    dummy_chunks = [
        {
            "chunk_id":    "test_chunk_0000",
            "text":        "Patient is a 45-year-old male presenting with chest pain radiating to the left arm. BP 160/100. ECG shows ST elevation in leads II, III, aVF.",
            "source":      "0003_Cardiology_sample.txt",
            "chunk_index": 0,
        },
        {
            "chunk_id":    "test_chunk_0001",
            "text":        "Assessment: Inferior STEMI. Plan: Emergent PCI. Start aspirin 325mg, heparin drip. Cardiology consult placed.",
            "source":      "0003_Cardiology_sample.txt",
            "chunk_index": 1,
        },
    ]

    result = summarize("What is the patient's diagnosis and treatment plan?", dummy_chunks)
    print("\n── Summary Output ──────────────────────────────")
    for key, val in result.items():
        print(f"\n{key.upper()}:\n{val}")