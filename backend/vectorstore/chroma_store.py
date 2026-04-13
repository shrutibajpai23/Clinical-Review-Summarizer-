"""
backend/vectorstore/chroma_store.py
ChromaDB vector store — persist, query, and manage clinical document embeddings.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

load_dotenv()

# ── Config 
CHROMA_DB_PATH  = os.getenv("CHROMA_DB_PATH",  "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "clinical_docs")


_client:     chromadb.PersistentClient | None = None
_collection: chromadb.Collection       | None = None


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False),
        )
    return _client


def _get_collection(name: str = COLLECTION_NAME) -> chromadb.Collection:
    global _collection
    if _collection is None or _collection.name != name:
        client      = _get_client()
        _collection = client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection




def add_chunks(chunks: list[dict], collection_name: str = COLLECTION_NAME) -> int:
    """
    Upsert embedded chunks into ChromaDB.

    Parameters
    ----------
    chunks : list of chunk dicts — must have 'chunk_id', 'text', 'embedding'
             plus any metadata fields from the agreed schema.

    Returns
    -------
    Number of chunks successfully added.
    """
    collection = _get_collection(collection_name)

    ids         = []
    embeddings  = []
    documents   = []
    metadatas   = []

    skipped = 0
    for chunk in chunks:
        if chunk.get("embedding") is None:
            skipped += 1
            continue

        ids.append(chunk["chunk_id"])
        embeddings.append(chunk["embedding"])
        documents.append(chunk["text"])
        metadatas.append(
            {
                "chunk_id":    chunk.get("chunk_id", ""),
                "chunk_index": chunk.get("chunk_index", 0),
                "total_chunks": chunk.get("total_chunks", 1),
                "source":      chunk.get("source", ""),
                "file_path":   chunk.get("file_path", ""),
                "doc_type":    chunk.get("doc_type", "general_clinical"),
                "page_count":  chunk.get("page_count", 1),
                "token_count": chunk.get("token_count", 0),
            }
        )

    if not ids:
        print("⚠️  No chunks with embeddings to add.")
        return 0

    # Upsert in batches of 100 to stay within ChromaDB limits
    batch_size = 100
    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        collection.upsert(
            ids        = ids[start:end],
            embeddings = embeddings[start:end],
            documents  = documents[start:end],
            metadatas  = metadatas[start:end],
        )

    added = len(ids)
    print(f"✅ Added {added} chunks to collection '{collection_name}' (skipped {skipped} without embeddings)")
    return added



def query(
    embedding:     list[float],
    n_results:     int         = 5,
    filter_source: str | None  = None,
    collection_name: str       = COLLECTION_NAME,
) -> list[dict]:
    """
    Query ChromaDB for the most similar chunks.

    Parameters
    ----------
    embedding     : query embedding vector
    n_results     : number of results to return
    filter_source : optional — filter by source filename (exact match)

    Returns
    -------
    List of result dicts with keys:
        chunk_id, text, score, source, file_path, doc_type,
        chunk_index, total_chunks, token_count, page_count
    """
    collection = _get_collection(collection_name)

    where = {"source": filter_source} if filter_source else None

    try:
        results = collection.query(
            query_embeddings=[embedding],
            n_results        = n_results,
            where            = where,
            include          = ["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        raise RuntimeError(f"ChromaDB query failed: {exc}") from exc

    output = []
    ids       = results["ids"][0]
    docs      = results["documents"][0]
    metas     = results["metadatas"][0]
    distances = results["distances"][0]

    for chunk_id, doc, meta, dist in zip(ids, docs, metas, distances):
        output.append(
            {
                "chunk_id":    chunk_id,
                "text":        doc,
                "score":       round(1 - dist, 4),   # cosine similarity
                "source":      meta.get("source", ""),
                "file_path":   meta.get("file_path", ""),
                "doc_type":    meta.get("doc_type", ""),
                "chunk_index": meta.get("chunk_index", 0),
                "total_chunks": meta.get("total_chunks", 1),
                "token_count": meta.get("token_count", 0),
                "page_count":  meta.get("page_count", 1),
            }
        )

    return output



def get_collection_stats(collection_name: str = COLLECTION_NAME) -> dict:
    """Return basic stats about the collection."""
    collection = _get_collection(collection_name)
    count      = collection.count()
    return {
        "collection_name": collection_name,
        "total_chunks":    count,
        "chroma_db_path":  CHROMA_DB_PATH,
    }


def delete_collection(name: str) -> None:
    """Delete a ChromaDB collection by name."""
    global _collection
    client = _get_client()
    client.delete_collection(name=name)
    if _collection and _collection.name == name:
        _collection = None
    print(f"🗑️  Deleted collection '{name}'")



if __name__ == "__main__":
    print("Stats:", get_collection_stats())