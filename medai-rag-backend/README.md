# MedAI‑RAG Backend

FastAPI backend implementing /ask and /ingest with FAISS vector search, local/OpenAI embeddings, and OpenAI (or mock) generation.

## Run
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env
python -m app.ingest --path data/sample_docs
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
