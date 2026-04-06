from backend.rag.retriever import retrieve
from backend.rag.summarizer import summarize

query = "What cardiac conditions were found in the patient?"

print("=" * 60)
print(f"QUERY: {query}")
print("=" * 60)

print("\n[Step 1] Retrieving relevant chunks...")
chunks = retrieve(query, n_results=2)

print("\n[Step 2] Generating clinical summary...")
result = summarize(query, chunks)

print("\n" + "=" * 60)
print("CLINICAL SUMMARY")
print("=" * 60)
print(result["summary"])

print("\n" + "=" * 60)
print("SOURCES USED")
print("=" * 60)
for s in result["sources"]:
    print(f"  - {s['source']} | chunk {s['chunk_index']} | similarity {s['similarity']}")

print(f"\nModel used: {result['model']}")