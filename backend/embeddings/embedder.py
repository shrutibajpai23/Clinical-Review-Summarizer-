"""
backend/embeddings/embedder.py
Embed text using HuggingFace sentence-transformers (free, runs locally).
Model: all-MiniLM-L6-v2 — fast, lightweight, 384-dimensional embeddings.
"""

from __future__ import annotations

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print("⏳ Loading embedding model (first time only) …")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Embedding model loaded")
    return _model


def embed_text(text: str) -> list[float]:
    text = text.replace("\n", " ").strip()
    model = _get_model()
    vector = model.encode(text, convert_to_numpy=True)
    return vector.tolist()


def embed_chunks(chunks: list[dict]) -> list[dict]:
    total = len(chunks)
    print(f"🔢 Embedding {total} chunks locally …")
    model = _get_model()
    texts = [chunk.get("text", "").replace("\n", " ").strip() for chunk in chunks]
    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        if not texts[i]:
            chunk["embedding"] = None
        else:
            chunk["embedding"] = vector.tolist()
    embedded = sum(1 for c in chunks if c.get("embedding") is not None)
    print(f"\n✅ Done — {embedded}/{total} chunks embedded successfully")
    return chunks