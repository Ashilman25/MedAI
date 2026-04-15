import os
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from ..models import ExpandRequest, ExpandResponse
from ..rag import answer
from ..ingest import fetch_pubmed_docs, ingest_text_items
from ..dependencies import limiter, get_current_uid, check_daily_limit
from ..logging_config import logger

router = APIRouter()


def _expand_synonyms(q: str) -> str:
    """
    Very small, clinical synonym expander for PubMed terms (safe defaults).
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


def _normalize_terms(terms: List[str]) -> List[str]:
    seen, out = set(), []
    for t in terms or []:
        tt = (t or "").strip()
        k = tt.lower()
        if tt and k not in seen:
            seen.add(k)
            out.append(tt)
    return out


def _query_from_terms(terms: List[str]) -> str:
    quoted = [f'"{t}"' if " " in t else t for t in terms]
    return " OR ".join(quoted)


_INTENT_EXPANSIONS = {
    "dosing_safety": ["adverse effects", "side effects", "complications"],
    "diagnosis": ["diagnosis", "screening", "criteria"],
    "therapy": ["therapy", "management", "treatment"],
    "prognosis": ["prognosis", "outcomes", "mortality"],
    "epidemiology": ["incidence", "prevalence", "epidemiology"],
    "general": [],
}


def _default_types_for_pass(pass_idx: int) -> list[str]:
    if pass_idx == 1:
        return ["Guideline", "Practice Guideline", "Systematic Review", "Review"]
    if pass_idx == 2:
        return ["Systematic Review", "Meta-Analysis", "Review", "Guideline"]
    return []


@router.post("/expand-sources", response_model=ExpandResponse)
@limiter.limit("5/minute")
def expand_sources(request: Request, req: ExpandRequest, uid: Optional[str] = Depends(get_current_uid)):
    """
    Wide/iterative expansion with PubMed, ingest, re-answer.
    Supports either a raw query (legacy) or structured query_terms + intent.
    """
    check_daily_limit(uid, "expand")
    env_types = [t.strip() for t in os.getenv("PUBMED_FILTER_TYPES", "Guideline,Review").split(",") if t.strip()]
    lang = req.lang or os.getenv("PUBMED_LANG", "en")
    base_mindate = req.mindate if req.mindate is not None else (int(os.getenv("PUBMED_MINDATE", "0")) or None)
    target_conf = req.target_confidence
    max_passes = req.max_passes
    per_pass_retmax = req.per_pass_retmax

    used_terms = False
    if req.query_terms and len(req.query_terms) > 0:
        terms = _normalize_terms(req.query_terms)
        base_query = _query_from_terms(terms)
        used_terms = True
    else:
        base_query = _expand_synonyms(req.query or "")

    intent = (req.intent or "general").strip().lower()
    if intent not in _INTENT_EXPANSIONS:
        intent = "general"

    total_found = total_added = total_skipped = 0
    last_answer = None
    passes_done = 0

    for passes_done in range(1, max_passes + 1):
        if req.types and passes_done == 1:
            types = req.types
        else:
            types = _default_types_for_pass(passes_done)

        if passes_done == 1:
            mindate = base_mindate
        elif passes_done == 2:
            mindate = base_mindate or 2015
        else:
            mindate = min(req.fallback_mindate, (base_mindate or req.fallback_mindate))

        q = base_query
        if passes_done == 2:
            extras = [w for w in _INTENT_EXPANSIONS.get(intent, []) if w.lower() not in q.lower()]
            if extras:
                q = f"({q}) OR ({' OR '.join(extras)})"
        if passes_done >= 3:
            cat = _INTENT_EXPANSIONS.get(intent, [])
            if cat:
                token = cat[0]
                if token.lower() not in q.lower():
                    q = f"({q}) OR {token}"

        retmax = per_pass_retmax * (1 if passes_done == 1 else 2 if passes_done == 2 else 3)

        pm_docs = fetch_pubmed_docs(
            query=q,
            retmax=retmax,
            mindate=mindate,
            maxdate=None,
            lang=lang,
            filter_types=types or None,
        )
        found = len(pm_docs)

        stats = ingest_text_items(pm_docs, owner_uid=uid)
        added = stats.get("added", 0)
        skipped = stats.get("skipped", 0)
        total_found += found
        total_added += added
        total_skipped += skipped

        last = answer(req.query or " ".join(req.query_terms or []), req.top_k)
        last_answer = last

        if (last["confidence"] >= target_conf) or (found == 0 and added == 0) or not req.wide:
            break

    if not last_answer:
        last_answer = answer(req.query or " ".join(req.query_terms or []), req.top_k)

    logger.info(json.dumps({
        "event": "expand_sources",
        "used_terms": used_terms,
        "intent": intent,
        "found": total_found,
        "added": total_added,
        "skipped": total_skipped,
        "passes": passes_done,
        "conf": float(last_answer.get("confidence", 0.0)),
    }))

    return ExpandResponse(
        answer=last_answer["answer"],
        citations=last_answer["citations"],
        confidence=last_answer["confidence"],
        found=total_found,
        added=total_added,
        skipped=total_skipped,
        passes=passes_done,
    )
