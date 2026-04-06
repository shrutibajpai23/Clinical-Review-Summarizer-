from backend.embeddings.embedder import embed_text, embed_query

print("Testing embed_text...")
vec = embed_text("Patient presented with allergic rhinitis and nasal congestion.")
print(f"Vector length: {len(vec)}")
print(f"First 5 values: {[round(v, 6) for v in vec[:5]]}")

print("\nTesting embed_query...")
qvec = embed_query("What are the patient's symptoms?")
print(f"Query vector length: {len(qvec)}")
print("\nEmbedder working correctly!")