# MedAI‑RAG (Monorepo: Frontend + Backend)

This package bundles both the **React + Vite frontend** and the **FastAPI backend**.
Use the steps below to run locally, or see the optional Docker Compose section.

## Quick Start (Two terminals)

### 1) Backend
```bash
cd medai-rag-backend
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env && nano .env
# Set (for local dev):
#   EMBEDDING_PROVIDER=sentence
#   MOCK_COMPLETIONS=true            # to develop without OpenAI
#   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
# Optional: ingest samples
python -m app.ingest --path data/sample_docs
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend (in new terminal)
```bash
cd medai-rag-frontend
npm install
npm install -D @vitejs/plugin-react
cp .env.example .env && nano .env
# Set:
#   VITE_API_BASE_URL=http://127.0.0.1:8000
#   VITE_MOCK_MODE=false
npm run dev
```
Open: http://localhost:5173

---

## Optional: Docker Compose (dev-ish)
```bash
docker compose up --build
```
- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173

> Note: The compose file uses a simple Node container for the Vite dev server. Hot reload works, but local node_modules are inside the container.

## Repo Layout
- `medai-rag-frontend/` — React + Vite + Tailwind UI for chat, citations, confidence
- `medai-rag-backend/` — FastAPI + FAISS (with NumPy fallback), ingestion, RAG pipeline
- `docker-compose.yml` — optional dev runner
