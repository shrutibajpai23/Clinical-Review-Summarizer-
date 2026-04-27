"""
backend/main.py
FastAPI — Clinical Review Summarizer v3.0
Endpoints: /upload /summarize /predict /analyze /history /health /ingest-bulk
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

from backend.ingestion.pipeline       import run_ingestion_pipeline
from backend.embeddings.embedder      import embed_chunks
from backend.vectorstore.chroma_store import add_chunks, get_collection_stats
from backend.rag.retriever            import retrieve
from backend.rag.summarizer           import summarize
from backend.rag.predictor            import predict

app = FastAPI(
    title       = "Clinical Review Summarizer API",
    description = "RAG-powered clinical summarization and timeline-aware disease risk prediction",
    version     = "3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods     = ["*"],
    allow_headers     = ["*"],
    allow_credentials = True,
)

query_history: list[dict] = []


# ── Shared request ─────────────────────────────────────────────────────────────
class BaseRequest(BaseModel):
    query:         str
    source_filter: Optional[str] = None
    n_results:     int           = 5
    use_mmr:       bool          = True


# ── /summarize ─────────────────────────────────────────────────────────────────
class SummarizeRequest(BaseRequest):
    pass

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


# ── /predict — timeline-aware models ──────────────────────────────────────────
class PredictRequest(BaseRequest):
    pass

class DocumentDate(BaseModel):
    raw_text:         str
    interpreted_date: str
    event:            str

class ConditionTimeline(BaseModel):
    trigger_date:    str
    onset_window:    str
    peak_date:       str
    resolution_date: str
    confidence:      str
    basis:           str

class PredictedCondition(BaseModel):
    condition:           str
    status:              str
    probability:         str
    trigger:             str
    timeline:            ConditionTimeline
    supporting_evidence: str
    citation:            str

class LifestyleChanges(BaseModel):
    diet:     str
    exercise: str
    sleep:    str
    habits:   str
    stress:   str

class FollowUpTest(BaseModel):
    test:             str
    reason:           str
    recommended_date: str
    frequency:        str

class PredictResponse(BaseModel):
    query:                       str
    document_dates:              list[DocumentDate]
    reference_date:              str
    risk_level:                  str
    risk_summary:                str
    predicted_conditions:        list[PredictedCondition]
    disease_progression_summary: str
    reasoning:                   str
    precautions:                 list[str]
    lifestyle_changes:           LifestyleChanges
    follow_up_tests:             list[FollowUpTest]
    data_gaps:                   str
    sources_used:                list[str]
    disclaimer:                  str
    model:                       str
    num_chunks_used:             int
    timestamp:                   str


# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    try:    stats = get_collection_stats()
    except: stats = {"error": "ChromaDB not yet initialised"}
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z", "chromadb": stats}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".txt", ".pdf", ".docx"}:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{suffix}'.")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"File save failed: {exc}")
    try:
        result   = run_ingestion_pipeline(tmp_path, save_chunks=False)
        chunks   = result["chunks"]
        doc_meta = result["doc_meta"]
        for chunk in chunks:
            chunk["source"] = file.filename
            chunk["file_path"] = file.filename
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")
    finally:
        os.unlink(tmp_path)
    if not chunks:
        raise HTTPException(status_code=422, detail="No chunks generated — file may be empty.")
    try:   chunks = embed_chunks(chunks)
    except Exception as exc: raise HTTPException(status_code=500, detail=f"Embedding failed: {exc}")
    try:   added = add_chunks(chunks)
    except Exception as exc: raise HTTPException(status_code=500, detail=f"Vector store failed: {exc}")
    return {
        "status": "success", "filename": file.filename,
        "doc_type": doc_meta.get("doc_type"), "chunks_added": added,
        "word_count": doc_meta.get("word_count"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_query(request: SummarizeRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        chunks = retrieve(query=request.query, source_filter=request.source_filter,
                          n_results=request.n_results, use_mmr=request.use_mmr)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {exc}")
    try:
        summary = summarize(request.query, chunks)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {exc}")
    ts = datetime.utcnow().isoformat() + "Z"
    summary["timestamp"] = ts
    query_history.append({
        "type": "summarize", "query": request.query, "timestamp": ts,
        "num_chunks_used": summary.get("num_chunks_used", 0),
        "sources_used":    summary.get("sources_used", []),
    })
    return SummarizeResponse(**summary)


@app.post("/predict", response_model=PredictResponse)
async def predict_query(request: PredictRequest):
    """
    Timeline-aware risk prediction.
    Extracts dates from the document and anchors every predicted condition
    to a real clinical event date — with onset window, peak, and resolution.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        chunks = retrieve(query=request.query, source_filter=request.source_filter,
                          n_results=request.n_results, use_mmr=request.use_mmr)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {exc}")
    try:
        prediction = predict(request.query, chunks)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")
    ts = datetime.utcnow().isoformat() + "Z"
    prediction["timestamp"] = ts
    query_history.append({
        "type":            "predict",
        "query":           request.query,
        "timestamp":       ts,
        "risk_level":      prediction.get("risk_level", "unknown"),
        "reference_date":  prediction.get("reference_date", "Not documented"),
        "num_chunks_used": prediction.get("num_chunks_used", 0),
        "sources_used":    prediction.get("sources_used", []),
    })
    return PredictResponse(**prediction)


@app.post("/analyze")
async def analyze_query(request: BaseRequest):
    """Summarize + timeline-predict in one call, sharing retrieval."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        chunks = retrieve(query=request.query, source_filter=request.source_filter,
                          n_results=request.n_results, use_mmr=request.use_mmr)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {exc}")
    try:    summary    = summarize(request.query, chunks)
    except Exception as exc: raise HTTPException(status_code=500, detail=f"Summarization failed: {exc}")
    try:    prediction = predict(request.query, chunks)
    except Exception as exc: raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")
    ts = datetime.utcnow().isoformat() + "Z"
    summary["timestamp"]    = ts
    prediction["timestamp"] = ts
    query_history.append({
        "type": "analyze", "query": request.query, "timestamp": ts,
        "risk_level":     prediction.get("risk_level", "unknown"),
        "reference_date": prediction.get("reference_date", "Not documented"),
        "num_chunks_used": len(chunks),
        "sources_used":   list(set(summary.get("sources_used",[]) + prediction.get("sources_used",[]))),
    })
    return {"query": request.query, "summary": summary, "prediction": prediction, "timestamp": ts}


@app.get("/history")
def get_history(limit: int = Query(default=20, ge=1, le=100)):
    return {"total": len(query_history), "history": list(reversed(query_history))[:limit]}

@app.delete("/history")
def clear_history():
    query_history.clear()
    return {"status": "cleared"}

@app.post("/ingest-bulk")
async def ingest_bulk(processed_dir: str = "data/processed"):
    processed_path = Path(processed_dir)
    if not processed_path.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {processed_dir}")
    json_files = list(processed_path.glob("*.json"))
    if not json_files:
        raise HTTPException(status_code=404, detail="No JSON chunk files found.")
    total_added, errors = 0, []
    for jf in json_files:
        try:
            chunks = json.loads(jf.read_text(encoding="utf-8"))
            chunks = embed_chunks(chunks)
            total_added += add_chunks(chunks)
        except Exception as exc:
            errors.append({"file": jf.name, "error": str(exc)})
    return {
        "status": "completed", "files_processed": len(json_files) - len(errors),
        "total_chunks_added": total_added, "errors": errors,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)