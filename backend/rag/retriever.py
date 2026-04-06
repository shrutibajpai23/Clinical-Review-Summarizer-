import os
from dotenv import load_dotenv
from backend.embeddings.embedder import embed_query
from backend.vectorstore.chroma_store import query_collection

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


def retrieve(query: str, n_results: int = 5, source_filter: str = None) -> list[dict]:
    """
    Full retrieval pipeline:
    1. Embed the user query
    2. Search ChromaDB for similar chunks
    3. Return ranked results with metadata
    """
    print(f"  [Retriever] Query: '{query[:60]}...' " if len(query) > 60 else f"  [Retriever] Query: '{query}'")

    query_embedding = embed_query(query)

    chunks = query_collection(
        query_embedding=query_embedding,
        n_results=n_results,
        source_filter=source_filter
    )

    print(f"  [Retriever] Retrieved {len(chunks)} chunks")
    for i, c in enumerate(chunks):
        print(f"    [{i+1}] {c['chunk_id']} | similarity: {c['similarity']}")

    return chunks