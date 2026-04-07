import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file!")

client = Groq(api_key=api_key)
CHAT_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a clinical AI assistant specializing in medical document analysis.

Given clinical document excerpts, produce a structured medical summary with EXACTLY these sections:

**Patient/Study Overview**
Brief overview of the patient or study subject.

**Key Findings**
The most important clinical findings from the documents.

**Diagnosis / Conclusions**
Primary diagnosis or conclusions drawn.

**Recommendations / Next Steps**
Suggested treatments, follow-ups, or actions.

**Limitations / Risks**
Any risks, limitations, or missing information.

Rules:
1. Base EVERY claim only on the provided document excerpts
2. If information is missing, write "Not mentioned in provided documents"
3. Never hallucinate medical facts
4. Be concise but clinically precise
5. Always mention the source document for key claims"""


def build_prompt(query: str, chunks: list[dict]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks):
        source = chunk["metadata"]["source"]
        context_parts.append(
            f"--- Excerpt {i+1} (Source: {source}) ---\n{chunk['text']}"
        )
    context = "\n\n".join(context_parts)

    return f"""Based on the following clinical document excerpts, answer this query:

QUERY: {query}

DOCUMENT EXCERPTS:
{context}

Provide a structured clinical summary following the format specified."""


def summarize(query: str, chunks: list[dict]) -> dict:
    """
    Generate a structured clinical summary using Groq Llama 3.
    """
    if not chunks:
        return {
            "summary": "No relevant documents found for this query.",
            "sources": [],
            "query":   query,
            "model":   CHAT_MODEL
        }

    prompt = build_prompt(query, chunks)
    print(f"  [Summarizer] Calling {CHAT_MODEL} via Groq...")

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.2,
        max_tokens=1500
    )

    summary_text = response.choices[0].message.content

    sources = [
        {
            "chunk_id":    c["chunk_id"],
            "source":      c["metadata"]["source"],
            "chunk_index": c["metadata"]["chunk_index"],
            "similarity":  c["similarity"],
            "text":        c["text"][:200]
        }
        for c in chunks
    ]

    return {
        "summary": summary_text,
        "sources": sources,
        "query":   query,
        "model":   CHAT_MODEL
    }