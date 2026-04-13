"""
backend/rag/retriever.py
Embed a query and retrieve top-k chunks from ChromaDB.
Supports MMR (Maximal Marginal Relevance) for result diversity.
"""

from __future__ import annotations

import os
import numpy as np
from dotenv import load_dotenv

from backend.embeddings.embedder     import embed_text
from backend.vectorstore.chroma_store import query as chroma_query

load_dotenv()

TOP_K = int(os.getenv("TOP_K_RESULTS", "5"))


# ── MMR helpers

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def _mmr(
    query_embedding: list[float],
    candidates:      list[dict],
    k:               int   = 5,
    lambda_mult:     float = 0.5,
) -> list[dict]:
    """
    Maximal Marginal Relevance re-ranking.

    Balances relevance to the query vs diversity among selected chunks.
    lambda_mult = 1.0 → pure relevance (no diversity)
    lambda_mult = 0.0 → pure diversity (no relevance)
    """
    if len(candidates) <= k:
        return candidates

    selected: list[dict]        = []
    remaining: list[dict]       = list(candidates)
    selected_embeddings: list   = []

    for _ in range(k):
        if not remaining:
            break

        best_score  = float("-inf")
        best_chunk  = None
        best_idx    = -1

        for i, chunk in enumerate(remaining):
            relevance = chunk.get("score", 0.0)

            if selected_embeddings:
                # penalty = max similarity to any already-selected chunk
                chunk_emb = chunk.get("_embedding", query_embedding)
                redundancy = max(
                    _cosine_similarity(chunk_emb, sel_emb)
                    for sel_emb in selected_embeddings
                )
            else:
                redundancy = 0.0

            mmr_score = lambda_mult * relevance - (1 - lambda_mult) * redundancy

            if mmr_score > best_score:
                best_score = mmr_score
                best_chunk = chunk
                best_idx   = i

        if best_chunk is not None:
            selected.append(best_chunk)
            selected_embeddings.append(best_chunk.get("_embedding", query_embedding))
            remaining.pop(best_idx)

    return selected


# ── Public API 

def retrieve(
    query:         str,
    source_filter: str | None = None,
    n_results:     int        = TOP_K,
    use_mmr:       bool       = True,
    mmr_lambda:    float      = 0.6,
    mmr_fetch_k:   int        = 20,
) -> list[dict]:
    """
    Full retrieval pipeline: embed query → search ChromaDB → (optional) MMR.

    Parameters
    ----------
    query         : user's natural language question
    source_filter : limit results to a specific source file
    n_results     : number of chunks to return
    use_mmr       : apply MMR re-ranking for diversity
    mmr_lambda    : MMR relevance weight (0–1); higher = more relevance
    mmr_fetch_k   : how many candidates to fetch before MMR filtering

    Returns
    -------
    List of chunk dicts with keys:
        chunk_id, text, score, source, file_path, doc_type,
        chunk_index, total_chunks, token_count, page_count
    """
    if not query.strip():
        raise ValueError("Query cannot be empty")

    # 1. Embed the query
    print(f"🔍 Retrieving for: '{query[:80]}{'…' if len(query) > 80 else ''}'")
    query_embedding = embed_text(query)

    # 2. Fetch candidates from ChromaDB
    fetch_k    = mmr_fetch_k if use_mmr else n_results
    candidates = chroma_query(
        embedding     = query_embedding,
        n_results     = fetch_k,
        filter_source = source_filter,
    )

    if not candidates:
        print("⚠️  No results found in ChromaDB.")
        return []

    # 3. MMR re-ranking
    if use_mmr and len(candidates) > n_results:

        chunks = _mmr(query_embedding, candidates, k=n_results, lambda_mult=mmr_lambda)
    else:
        chunks = candidates[:n_results]

    print(f"✅ Retrieved {len(chunks)} chunks")
    for i, c in enumerate(chunks, 1):
        print(f"   [{i}] score={c['score']:.4f}  source={c['source']}")

    return chunks



if __name__ == "__main__":
    results = retrieve("What is the patient's diagnosis?", n_results=3)
    if results:
        print("\nTop result text preview:")
        print(results[0]["text"][:300])
    else:
        print("No results — make sure ChromaDB has been populated first.")