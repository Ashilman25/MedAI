# 🧠 MedAI-RAG

# MedAI-RAG is an AI-powered medical reference assistant that provides grounded, cited answers 
# to clinical questions. It is a full-stack application featuring a React frontend and a FastAPI backend, 
# implementing a Retrieval-Augmented Generation (RAG) pipeline to ensure responses are based on 
# a supplied knowledge base.

# The system can ingest medical literature from local files (PDFs, text files) and directly from PubMed, 
# building a searchable vector index. When a user asks a question, the system retrieves relevant text chunks, 
# which are then passed to a large language model to synthesize an evidence-based answer, 
# complete with citations and a confidence score.


# --------------------------------------------------------
# 🚀 Key Features
# --------------------------------------------------------
# • Retrieval-Augmented Generation (RAG)
# • Dynamic Source Ingestion (local files + PubMed)
# • Interactive Chat UI with source citations
# • Confidence scoring and PubMed expansion
# • Firebase authentication or Guest mode
# • FastAPI + FAISS backend for efficient search
# --------------------------------------------------------


# --------------------------------------------------------
# 📁 Repository Layout
# --------------------------------------------------------
# medai-rag-frontend/   → React + Vite frontend (Chat, Upload, Docs)
# medai-rag-backend/    → FastAPI backend (RAG pipeline, ingestion)
# docker-compose.yml    → Run both services together for local dev
# --------------------------------------------------------


# --------------------------------------------------------
# 🧩 Backend Details
# --------------------------------------------------------
# Framework: FastAPI
# Vector Search: FAISS (NumPy fallback)
# Embeddings: sentence-transformers or OpenAI
# LLM Completions: OpenAI or mock
# Data Ingestion: pypdf, biopython (PubMed)

# 🔌 API Endpoints
# POST /ask             → Ask a question, get answer + citations
# POST /ingest          → Upload and process local documents
# POST /expand-sources  → Auto-search PubMed for better context
# GET  /documents       → List all indexed documents
# GET  /health          → Simple health check

# 📚 Ingestion Options
# 1. Local files (PDFs, TXT, CSV) → via /upload
# 2. PubMed → via CLI or expand-sources endpoint

# --------------------------------------------------------
# 💻 Frontend Details
# --------------------------------------------------------
# Framework: React + Vite
# Styling: Tailwind CSS
# Animations: Framer Motion
# Routing: React Router
# State: Firebase (auth) or localStorage (guest)

# 🔧 Frontend Pages
# • /chat  → Ask questions, view answers + sources
# • /docs  → Browse indexed documents
# • /upload → Add PDFs or text documents
# • /login → Firebase auth 

# --------------------------------------------------------
# ⚠️ Disclaimer
# --------------------------------------------------------
# This application is for educational and research purposes only.
# It is NOT intended for patient use or medical decision-making.
# Always verify information against trusted primary sources.
