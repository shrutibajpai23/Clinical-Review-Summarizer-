"""
End-to-end ingestion: file path → cleaned chunks ready for embedding.
"""

from __future__ import annotations

from pathlib import Path

from backend.ingestion.loader  import load_document
from backend.ingestion.cleaner import clean_text, detect_doc_type
from backend.ingestion.chunker import chunk_document, save_chunks_to_json


def run_ingestion_pipeline(
    file_path: str | Path,
    save_chunks: bool = True,
    chunk_size: int   = 512,
    overlap: int      = 50,
) -> dict:
  
   
    print(f"Loading: {file_path}")
    doc = load_document(file_path)

    
    doc["raw_text"] = clean_text(doc["raw_text"])


    doc["doc_type"] = detect_doc_type(doc["filename"], doc["raw_text"])
    print(f"   doc_type detected: {doc['doc_type']}")

    
    chunks = chunk_document(doc, chunk_size=chunk_size, overlap=overlap)
    print(f"   chunks created: {len(chunks)}")

   
    if save_chunks and chunks:
        saved_path = save_chunks_to_json(chunks)
        print(f"   saved → {saved_path}")


    doc_meta = {k: v for k, v in doc.items() if k != "raw_text"}

    return {"doc_meta": doc_meta, "chunks": chunks}


def run_batch_pipeline(
    directory: str | Path,
    extensions: list[str] | None = None,
    save_chunks: bool = True,
    chunk_size: int   = 512,
    overlap: int      = 50,
) -> list[dict]:
    """
    Run the ingestion pipeline over every supported file in *directory*.

    Returns a list of pipeline result dicts (one per file).
    """
    allowed = set(extensions or [".txt", ".pdf", ".docx"])
    results: list[dict] = []

    files = sorted(
        f for f in Path(directory).iterdir()
        if f.is_file() and f.suffix.lower() in allowed
    )

    print(f"\n Batch pipeline — {len(files)} files found in '{directory}'")

    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}]", end=" ")
        try:
            result = run_ingestion_pipeline(
                file_path,
                save_chunks=save_chunks,
                chunk_size=chunk_size,
                overlap=overlap,
            )
            results.append(result)
        except Exception as exc:
            print(f"⚠️  Error processing {file_path.name}: {exc}")

    total_chunks = sum(len(r["chunks"]) for r in results)
    print(f"\n✅ Batch done — {len(results)} files | {total_chunks} total chunks")
    return results


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
    results = run_batch_pipeline(target)
    if results:
        first = results[0]
        print("\nSample doc_meta:", first["doc_meta"])
        print("First chunk_id:", first["chunks"][0]["chunk_id"])