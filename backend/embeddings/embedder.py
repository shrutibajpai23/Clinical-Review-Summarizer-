import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

client = genai.Client(api_key=api_key)

EMBEDDING_MODEL = "models/gemini-embedding-2-preview"
MAX_RETRIES = 3
RETRY_DELAY = 2


def embed_text(text: str) -> list[float]:
    """
    Embed a single string using Gemini embedding model.
    Returns a list of floats.
    """
    for attempt in range(MAX_RETRIES):
        try:
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text.strip(),
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
            )
            return result.embeddings[0].values

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"  [Retry {attempt+1}] Embedding failed: {e}")
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError(f"Embedding failed after {MAX_RETRIES} attempts: {e}")


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Add an 'embedding' field to each chunk dict.
    """
    print(f"Embedding {len(chunks)} chunks using {EMBEDDING_MODEL}...")
    embedded = []

    for i, chunk in enumerate(chunks):
        print(f"  [{i+1}/{len(chunks)}] Embedding: {chunk['chunk_id']}")
        embedding = embed_text(chunk["text"])
        embedded_chunk = {**chunk, "embedding": embedding}
        embedded.append(embedded_chunk)

        if i > 0 and i % 10 == 0:
            time.sleep(0.5)

    print(f"Done. {len(embedded)} chunks embedded.")
    return embedded


def embed_query(query: str) -> list[float]:
    """
    Embed a user query for similarity search.
    """
    for attempt in range(MAX_RETRIES):
        try:
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=query.strip(),
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
            )
            return result.embeddings[0].values

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"  [Retry {attempt+1}] Query embedding failed: {e}")
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError(f"Query embedding failed after {MAX_RETRIES} attempts: {e}")