import os
import chromadb
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "clinical_docs"


def get_client():
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)


def get_collection():
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def add_chunks(chunks: list[dict]) -> dict:
    """
    Store embedded chunks into ChromaDB.
    Each chunk must have: chunk_id, text, embedding, source, doc_type
    """
    collection = get_collection()

    ids        = [c["chunk_id"]   for c in chunks]
    documents  = [c["text"]       for c in chunks]
    embeddings = [c["embedding"]  for c in chunks]
    metadatas  = [
        {
            "source":       c["source"],
            "doc_type":     c["doc_type"],
            "chunk_index":  c["chunk_index"],
            "total_chunks": c["total_chunks"],
            "file_path":    c["file_path"],
        }
        for c in chunks
    ]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return {
        "status": "success",
        "chunks_stored": len(chunks),
        "collection": COLLECTION_NAME
    }


def query_collection(query_embedding: list[float], n_results: int = 5, source_filter: str = None) -> list[dict]:
    """
    Search ChromaDB for most similar chunks to a query embedding.
    Optionally filter by source filename.
    """
    collection = get_collection()

    where = {"source": source_filter} if source_filter else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "chunk_id":    results["ids"][0][i],
            "text":        results["documents"][0][i],
            "metadata":    results["metadatas"][0][i],
            "distance":    results["distances"][0][i],
            "similarity":  round(1 - results["distances"][0][i], 4)
        })

    return chunks


def get_stats() -> dict:
    """
    Return collection statistics.
    """
    collection = get_collection()
    count = collection.count()
    return {
        "collection": COLLECTION_NAME,
        "total_chunks": count,
        "db_path": CHROMA_DB_PATH
    }


def delete_collection() -> dict:
    """
    Wipe the entire collection (use carefully).
    """
    client = get_client()
    client.delete_collection(name=COLLECTION_NAME)
    return {"status": "deleted", "collection": COLLECTION_NAME}