"""
backend/main.py
FastAPI application — Clinical Review Summarizer backend.
Endpoints: /upload, /summarize, /history, /health
"""

from __future__ import annotations

import os
import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

# ── Import pipeline modules
from backend.ingestion.pipeline       import run_ingestion_pipeline
from backend.embeddings.embedder      import embed_chunks
from backend.vectorstore.chroma_store import add_chunks, get_collection_stats
from backend.rag.retriever            import retrieve
from backend.rag.summarizer           import summarize

# ── App setup 
app = FastAPI(
    title       = "Clinical Review Summarizer API",
    description = "RAG-powered clinical document summarization",
    version     = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
    allow_credentials = True,
)

# ── In-memory session history (v1 — no database) 
query_history: list[dict] = []


# ── Request / Response models

class SummarizeRequest(BaseModel):
    query:         str
    source_filter: Optional[str] = None
    n_results:     int           = 5
    use_mmr:       bool          = True


class SummarizeResponse(BaseModel):
    query:           str
    overview:        str
    key_findings:    str
    diagnosis:       str
    recommendations: str
    limitations:     str
    sources_used:    list[str]
    model:           str
    num_chunks_used: int
    timestamp:       str


# ── Endpoints 

@app.get("/health")
def health_check():
    """Basic health check — confirms API is running."""
    try:
        stats = get_collection_stats()
    except Exception:
        stats = {"error": "ChromaDB not yet initialised"}

    return {
        "status":    "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "chromadb":  stats,
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a clinical document (.txt / .pdf / .docx).
    Runs full ingestion pipeline → embed → store in ChromaDB.
    """
    allowed_extensions = {".txt", ".pdf", ".docx"}
    suffix = Path(file.filename).suffix.lower()

    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code = 400,
            detail      = f"Unsupported file type '{suffix}'. Allowed: {allowed_extensions}",
        )

    # Save upload to a temp file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"File save failed: {exc}")

    # Run ingestion pipeline
    try:
        result = run_ingestion_pipeline(tmp_path, save_chunks=False)
        chunks = result["chunks"]
        doc_meta = result["doc_meta"]

        # Patch source filename to the original uploaded name
        for chunk in chunks:
            chunk["source"]   = file.filename
            chunk["file_path"] = file.filename

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")
    finally:
        os.unlink(tmp_path)   # clean up temp file

    if not chunks:
        raise HTTPException(status_code=422, detail="No chunks generated — file may be empty.")

    # Embed chunks
    try:
        chunks = embed_chunks(chunks)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {exc}")

    # Store in ChromaDB
    try:
        added = add_chunks(chunks)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Vector store failed: {exc}")

    return {
        "status":       "success",
        "filename":     file.filename,
        "doc_type":     doc_meta.get("doc_type"),
        "chunks_added": added,
        "word_count":   doc_meta.get("word_count"),
        "timestamp":    datetime.utcnow().isoformat() + "Z",
    }


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_query(request: SummarizeRequest):
    """
    Accept a clinical query, retrieve relevant chunks via RAG,
    and return a structured GPT-4 summary.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Retrieve relevant chunks
    try:
        chunks = retrieve(
            query         = request.query,
            source_filter = request.source_filter,
            n_results     = request.n_results,
            use_mmr       = request.use_mmr,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {exc}")

    # Generate summary
    try:
        summary = summarize(request.query, chunks)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {exc}")

    timestamp = datetime.utcnow().isoformat() + "Z"
    summary["timestamp"] = timestamp

    # Save to session history
    query_history.append(
        {
            "query":           request.query,
            "timestamp":       timestamp,
            "num_chunks_used": summary.get("num_chunks_used", 0),
            "sources_used":    summary.get("sources_used", []),
        }
    )

    return SummarizeResponse(**summary)


@app.get("/history")
def get_history(limit: int = Query(default=20, ge=1, le=100)):
    """Return the session's query history (most recent first)."""
    return {
        "total":   len(query_history),
        "history": list(reversed(query_history))[:limit],
    }


@app.delete("/history")
def clear_history():
    """Clear the in-memory query history."""
    query_history.clear()
    return {"status": "cleared"}




@app.post("/ingest-bulk")
async def ingest_bulk(processed_dir: str = "data/processed"):
    """
    Load all pre-processed JSON chunk files from data/processed/
    and store them in ChromaDB. Useful for initial data loading.
    """
    processed_path = Path(processed_dir)
    if not processed_path.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {processed_dir}")

    json_files = list(processed_path.glob("*.json"))
    if not json_files:
        raise HTTPException(status_code=404, detail="No JSON chunk files found.")

    total_added = 0
    errors      = []

    for json_file in json_files:
        try:
            chunks = json.loads(json_file.read_text(encoding="utf-8"))
            chunks = embed_chunks(chunks)
            added  = add_chunks(chunks)
            total_added += added
        except Exception as exc:
            errors.append({"file": json_file.name, "error": str(exc)})

    return {
        "status":      "completed",
        "files_processed": len(json_files) - len(errors),
        "total_chunks_added": total_added,
        "errors":      errors,
        "timestamp":   datetime.utcnow().isoformat() + "Z",
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)