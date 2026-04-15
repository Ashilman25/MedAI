import json
from typing import Optional
from fastapi import APIRouter, Depends, Request
from ..models import AskRequest, AskResponse, SuggestTermsReq, SuggestTermsResp
from ..rag import answer, get_store, get_embedder
from ..dependencies import limiter, get_current_uid, check_daily_limit
from ..logging_config import logger

router = APIRouter()


@router.get("/health")
def health():
    checks = {"store_loaded": False, "embedding_ready": False}
    try:
        store = get_store()
        checks["store_loaded"] = True
        checks["doc_count"] = store.size()
    except Exception:
        pass
    try:
        embedder = get_embedder()
        checks["embedding_ready"] = embedder is not None
        checks["embedding_provider"] = embedder.provider
    except Exception:
        pass
    ok = checks["store_loaded"] and checks["embedding_ready"]
    return {"ok": ok, **checks}


@router.post("/ask", response_model=AskResponse)
@limiter.limit("20/minute")
def ask(request: Request, req: AskRequest, uid: Optional[str] = Depends(get_current_uid)):
    check_daily_limit(uid, "ask")
    return AskResponse(**answer(req.query, req.top_k))


@router.post("/suggest-terms", response_model=SuggestTermsResp)
@limiter.limit("20/minute")
def suggest_terms(request: Request, req: SuggestTermsReq, uid: Optional[str] = Depends(get_current_uid)):
    check_daily_limit(uid, "ask")
    from ..query_suggest import extract_terms_and_intent
    terms, intent, method = extract_terms_and_intent(req.message)
    logger.info(json.dumps({"event": "suggest_terms", "len_msg": len(req.message or ""), "terms": terms, "intent": intent, "method": method}))
    return SuggestTermsResp(terms=terms, intent=intent, method=method)
