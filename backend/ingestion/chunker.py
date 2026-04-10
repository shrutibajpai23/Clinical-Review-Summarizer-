"""
Token-aware chunking using tiktoken.
Produces chunks that exactly match the schema Member 1's ChromaDB store expects.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import tiktoken


ENCODING_NAME  = "cl100k_base"   # used by GPT-4 / text-embedding-3-small
CHUNK_SIZE     = 512             # tokens per chunk
CHUNK_OVERLAP  = 50              # tokens of overlap between consecutive chunks
PROCESSED_DIR  = Path("data/processed")



def _get_encoder() -> tiktoken.Encoding:
    return tiktoken.get_encoding(ENCODING_NAME)


def _safe_stem(filename: str) -> str:
    """Return a filesystem-safe version of the filename stem for chunk IDs."""
    stem = Path(filename).stem
    stem = re.sub(r"[^\w]", "_", stem)
    return stem[:40]


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """
    Split *text* into token-bounded chunks with overlap.

    Returns a list of dicts:
        { text: str, token_count: int, chunk_index: int, total_chunks: int }
    (caller adds chunk_id, source, file_path, doc_type, page_count)
    """
    enc    = _get_encoder()
    tokens = enc.encode(text)

    if not tokens:
        return []

    raw_chunks: list[list[int]] = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        raw_chunks.append(tokens[start:end])
        if end >= len(tokens):
            break
        start += chunk_size - overlap   # slide forward with overlap

    chunks = []
    for idx, token_chunk in enumerate(raw_chunks):
        chunk_text_str = enc.decode(token_chunk)
        chunks.append(
            {
                "text":        chunk_text_str,
                "token_count": len(token_chunk),
                "chunk_index": idx,
                "total_chunks": len(raw_chunks),
            }
        )

    return chunks


def chunk_document(
    doc: dict,
    chunk_size: int = CHUNK_SIZE,
    overlap: int    = CHUNK_OVERLAP,
) -> list[dict]:
    """
    Chunk a loaded+cleaned document dict (from loader + cleaner) and attach
    the full metadata schema required by Member 1's ChromaDB store.

    Parameters
    ----------
    doc : dict with at least:
        raw_text, filename, file_path, page_count, doc_type

    Returns
    -------
    List of chunk dicts matching the agreed schema:
    {
        chunk_id, text, token_count, chunk_index, total_chunks,
        source, file_path, doc_type, page_count
    }
    """
    raw_text   = doc.get("raw_text", "")
    filename   = doc.get("filename", "unknown.txt")
    file_path  = doc.get("file_path", "")
    page_count = doc.get("page_count", 1)
    doc_type   = doc.get("doc_type", "general_clinical")

    base_chunks = chunk_text(raw_text, chunk_size, overlap)
    stem        = _safe_stem(filename)

    final_chunks = []
    for chunk in base_chunks:
        idx       = chunk["chunk_index"]
        chunk_id  = f"{stem}_chunk_{str(idx).zfill(4)}"
        final_chunks.append(
            {
                "chunk_id":    chunk_id,
                "text":        chunk["text"],
                "token_count": chunk["token_count"],
                "chunk_index": idx,
                "total_chunks": chunk["total_chunks"],
                "source":      filename,
                "file_path":   file_path,
                "doc_type":    doc_type,
                "page_count":  page_count,
            }
        )

    return final_chunks


def save_chunks_to_json(chunks: list[dict], output_path: str | Path | None = None) -> Path:
    """
    Persist chunks to a JSON file under data/processed/.
    If *output_path* is None, derive filename from the first chunk's source.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        source   = chunks[0]["source"] if chunks else "unknown"
        stem     = _safe_stem(source)
        out_file = PROCESSED_DIR / f"{stem}_chunks.json"
    else:
        out_file = Path(output_path)

    out_file.write_text(json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_file


def load_chunks_from_json(json_path: str | Path) -> list[dict]:
    """Read previously saved chunks from a JSON file."""
    return json.loads(Path(json_path).read_text(encoding="utf-8"))



if __name__ == "__main__":
    sample_doc = {
        "filename":   "0001_Allergy_sample.txt",
        "file_path":  "data/raw/0001_Allergy_sample.txt",
        "page_count": 1,
        "doc_type":   "doctor_note",
        "raw_text":   (
            "Patient presented with seasonal allergic rhinitis. "
            "HISTORY: Symptoms began 3 years ago. "
            "PHYSICAL EXAM: Pale nasal mucosa, watery discharge. "
            "PLAN: Loratadine 10 mg daily, follow-up in 4 weeks. "
        ) * 50,   # ~2 000 words → several chunks
    }

    chunks = chunk_document(sample_doc)
    print(f"Generated {len(chunks)} chunks")
    print("First chunk keys:", list(chunks[0].keys()))
    print("First chunk_id:", chunks[0]["chunk_id"])
    print("Token count:", chunks[0]["token_count"])

    saved = save_chunks_to_json(chunks)
    print("Saved to:", saved)