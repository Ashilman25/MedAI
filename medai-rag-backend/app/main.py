import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .config import get_settings
from .models import AskRequest, AskResponse, IngestResponse
from .ingest import ingest_paths
from .rag import answer
from app.rag import get_embedder, provider_signature
from app.vectorstore.faiss_store import FaissStore


s = get_settings()
app = FastAPI(title="MedAI‑RAG Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=s.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health(): return {"ok": True}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest): return AskResponse(**answer(req.query, req.top_k))

@app.post("/ingest", response_model=IngestResponse)
async def ingest(files: List[UploadFile] = File(...)):
    upload_dir = os.path.join(s.STORAGE_DIR, "_uploads"); os.makedirs(upload_dir, exist_ok=True)
    paths = []
    for f in files:
        dest = os.path.join(upload_dir, f.filename)
        with open(dest, "wb") as out: out.write(await f.read())
        paths.append(dest)
    res = ingest_paths(paths)
    return IngestResponse(**res)


@app.get("/documents")
def list_docs():
    """
    List all documents currently indexed (local + PubMed).
    """
    s = get_settings()
    embedder = get_embedder()
    store = FaissStore(s.STORAGE_DIR, embedder.dim, provider_signature(embedder))

    try:
        # store._meta is a list of all metadata dictionaries
        docs = []
        for md in getattr(store, "_meta", []):
            docs.append({
                "title": md.get("title"),
                "url": md.get("url"),
                "source": md.get("source", "unknown"),
                "pmid": md.get("pmid", None),
                "journal": md.get("journal", None),
                "year": md.get("year", None),
                "snippet": md.get("snippet", "")[:180]
            })
        return {"count": len(docs), "docs": docs}
    except Exception as e:
        return {"error": str(e)}

