from backend.embeddings.embedder import embed_text, embed_query
from backend.vectorstore.chroma_store import add_chunks, query_collection, get_stats

# Step 1 — create 2 fake chunks with real embeddings
print("Creating test chunks...")
chunks = [
    {
        "chunk_id":    "test_chunk_0001",
        "text":        "Patient presented with severe allergic rhinitis, nasal congestion, and sneezing.",
        "chunk_index":  0,
        "total_chunks": 2,
        "source":      "test_doc.txt",
        "file_path":   "data/raw/test_doc.txt",
        "doc_type":    "doctor_note",
        "page_count":   1,
    },
    {
        "chunk_id":    "test_chunk_0002",
        "text":        "Echocardiogram revealed mild left ventricular hypertrophy with preserved ejection fraction.",
        "chunk_index":  1,
        "total_chunks": 2,
        "source":      "test_doc.txt",
        "file_path":   "data/raw/test_doc.txt",
        "doc_type":    "doctor_note",
        "page_count":   1,
    }
]

# Step 2 — embed them
print("Embedding chunks...")
for chunk in chunks:
    chunk["embedding"] = embed_text(chunk["text"])

# Step 3 — store in ChromaDB
print("Storing in ChromaDB...")
result = add_chunks(chunks)
print(f"Stored: {result}")

# Step 4 — query
print("\nQuerying: 'What are the cardiac findings?'")
query_vec = embed_query("What are the cardiac findings?")
results = query_collection(query_vec, n_results=2)

for r in results:
    print(f"\n  Chunk: {r['chunk_id']}")
    print(f"  Similarity: {r['similarity']}")
    print(f"  Text: {r['text'][:80]}...")

# Step 5 — stats
print(f"\nDB Stats: {get_stats()}")
print("\nChromaDB working correctly!")