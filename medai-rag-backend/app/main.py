import os
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from .config import get_settings
from .models import AskRequest, AskResponse, IngestResponse
from .ingest import ingest_paths
from .rag import answer
from app.rag import get_embedder, provider_signature
from app.vectorstore.faiss_store import FaissStore
from .models import ExpandRequest, ExpandResponse
from .ingest import fetch_pubmed_docs, ingest_text_items


s = get_settings()
app = FastAPI(title="MedAI‑RAG Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=s.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _expand_synonyms(q: str) -> str:
    """
    Very small, clinical synonym expander for PubMed terms (safe defaults).
    You can extend this over time or make it MeSH-aware later.
    """
    syn = {
        "doac": "direct oral anticoagulant",
        "af": "atrial fibrillation",
        "htn": "hypertension",
        "t2dm": "type 2 diabetes",
        "mi": "myocardial infarction",
        "nsaid": "nonsteroidal anti-inflammatory drug",
        "copd": "chronic obstructive pulmonary disease",
        "pe": "pulmonary embolism",
        "dvt": "deep vein thrombosis",
        "uti": "urinary tract infection",
        "hf": "heart failure",
    }
    q_low = q.lower()
    extra = []
    for k, v in syn.items():
        if k in q_low and v not in q_low:
            extra.append(v)
    return q if not extra else f"{q} {' '.join(extra)}"


def _default_types_for_pass(pass_idx: int) -> list[str]:
    # Tight to broad
    if pass_idx == 1:
        return ["Guideline", "Practice Guideline", "Systematic Review", "Review"]
    if pass_idx == 2:
        return ["Systematic Review", "Meta-Analysis", "Review", "Guideline"]
    # Final pass: go broad (no filter)
    return []

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
def list_docs(uid: Optional[str] = Query(default=None)):
    """
    List documents indexed.

    - If uid provided: return docs owned by uid OR global docs (no owner_uids).
    - If uid not provided: return only global docs.
    """
    s = get_settings()
    embedder = get_embedder()
    store = FaissStore(s.STORAGE_DIR, embedder.dim, provider_signature(embedder))

    try:
        docs = []
        for md in getattr(store, "_meta", []):
            owners = md.get("owner_uids") or []

            if uid:
                # Include global docs (no owners) OR docs owned by this uid
                if owners and uid not in owners:
                    continue
            else:
                # Guest: only include global docs (no owners)
                if owners:
                    continue

            docs.append({
                "title": md.get("title"),
                "url": md.get("url"),
                "source": md.get("source", "unknown"),
                "pmid": md.get("pmid", None),
                "journal": md.get("journal", None),
                "year": md.get("year", None),
                "snippet": (md.get("snippet", "") or "")[:180],
            })
        return {"count": len(docs), "docs": docs}
    except Exception as e:
        return {"error": str(e)}


@app.post("/expand-sources", response_model=ExpandResponse)
def expand_sources(req: ExpandRequest):
    """
    Wide/iterative expansion with PubMed, ingest, re-answer.
    """
    # env defaults
    env_types = [t.strip() for t in os.getenv("PUBMED_FILTER_TYPES", "Guideline,Review").split(",") if t.strip()]
    lang = req.lang or os.getenv("PUBMED_LANG", "en")
    base_mindate = req.mindate if req.mindate is not None else (int(os.getenv("PUBMED_MINDATE", "0")) or None)
    target_conf = req.target_confidence
    max_passes = max(1, int(req.max_passes))
    per_pass_retmax = max(10, int(req.per_pass_retmax))



    # base query (with small synonym boost)
    base_query = _expand_synonyms(req.query)

    total_found = total_added = total_skipped = 0
    last_answer = None

    for p in range(1, max_passes + 1):
        # pass-specific shaping
        if req.types and p == 1:
            types = req.types
        else:
            types = _default_types_for_pass(p)

        # widen date on later passes
        if p == 1:
            mindate = base_mindate
        elif p == 2:
            mindate = base_mindate or 2015
        else:
            mindate = min(req.fallback_mindate, (base_mindate or req.fallback_mindate))

        # widen query slightly on later passes
        q = base_query
        if p == 2 and all(w not in q.lower() for w in ["therapy", "management", "treatment"]):
            q = f"{q} therapy management"
        if p >= 3 and "diagnosis" not in q.lower():
            q = f"{q} diagnosis"

        retmax = per_pass_retmax * (1 if p == 1 else 2 if p == 2 else 3)

        # 1) fetch
        pm_docs = fetch_pubmed_docs(
            query=q,
            retmax=retmax,
            mindate=mindate,
            maxdate=None,
            lang=lang,
            filter_types=types or None,
        )
        found = len(pm_docs)

        # 2) ingest (dedup by pmid), tag owner
        stats = ingest_text_items(pm_docs, owner_uid=req.owner_uid)
        added = stats.get("added", 0)
        skipped = stats.get("skipped", 0)
        total_found += found
        total_added += added
        total_skipped += skipped

        # 3) re-answer
        last = answer(req.query, req.top_k)
        last_answer = last

        # early exit
        if (last["confidence"] >= target_conf) or (found == 0 and added == 0) or not req.wide:
            break



    if not last_answer:
        last_answer = answer(req.query, req.top_k)

    return ExpandResponse(
        answer=last_answer["answer"],
        citations=last_answer["citations"],
        confidence=last_answer["confidence"],
        found=total_found,
        added=total_added,
        skipped=total_skipped,
        passes=min(max_passes, p),
    )