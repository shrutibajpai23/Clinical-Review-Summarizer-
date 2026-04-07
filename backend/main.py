import os
import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import aiofiles

load_dotenv()

from backend.embeddings.embedder import embed_chunks, embed_query
from backend.vectorstore.chroma_store import add_chunks, query_collection, get_stats
from backend.rag.retriever import retrieve
from backend.rag.summarizer import summarize

app = FastAPI(
    title="Clinical Review Summarizer API",
    description="RAG-powered clinical document summarization using Groq Llama 3",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session history
query_history = []

UPLOAD_DIR = "data/raw"
os.makedirs(UPLOAD_DIR, exist_ok=True)


#Request Models
class SummarizeRequest(BaseModel):
    query: str
    filename: str = None
    n_results: int = 5


# Routes 
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Clinical Review Summarizer API is running"}


@app.get("/stats")
def db_stats():
    return get_stats()


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a clinical document, chunk it, embed it, store in ChromaDB.
    Supports: .txt, .pdf, .docx
    """
    allowed_extensions = {".txt", ".pdf", ".docx"}
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {allowed_extensions}"
        )

    # Save file to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    try:
        # Import here to avoid circular imports
        from backend.ingestion.pipeline import run_ingestion_pipeline

        # Run ingestion pipeline
        result = run_ingestion_pipeline(file_path, save_to_disk=True)
        chunks = result["chunks"]
        doc_meta = result["doc_meta"]

        # Embed all chunks
        embedded_chunks = embed_chunks(chunks)

        # Store in ChromaDB
        store_result = add_chunks(embedded_chunks)

        return {
            "status":        "success",
            "filename":      file.filename,
            "doc_type":      doc_meta["doc_type"],
            "page_count":    doc_meta["page_count"],
            "word_count":    doc_meta["word_count"],
            "chunk_count":   doc_meta["chunk_count"],
            "chunks_stored": store_result["chunks_stored"],
            "message":       f"Document ingested and stored successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/summarize")
async def summarize_document(request: SummarizeRequest):
    """
    Query the RAG pipeline and return a structured clinical summary.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    start_time = time.time()

    try:
        # Retrieve relevant chunks
        chunks = retrieve(
            query=request.query,
            n_results=request.n_results,
            source_filter=request.filename
        )

        # Generate summary
        result = summarize(query=request.query, chunks=chunks)

        latency = round(time.time() - start_time, 2)

        # Save to history
        query_history.append({
            "query":     request.query,
            "filename":  request.filename,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "latency":   latency,
            "model":     result["model"]
        })

        return {
            "query":    request.query,
            "summary":  result["summary"],
            "sources":  result["sources"],
            "model":    result["model"],
            "latency":  latency
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@app.get("/history")
def get_history():
    """Return session query history."""
    return {
        "history": query_history,
        "total":   len(query_history)
    }


@app.delete("/history")
def clear_history():
    """Clear session query history."""
    query_history.clear()
    return {"status": "cleared"}