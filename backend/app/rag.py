import json
import time
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
from .config import get_settings
from .logging_config import warn
from .vectorstore.faiss_store import FaissStore

@dataclass
class Embedder:
    name: str
    provider: str
    dim: int
    _model: any = None
    def encode(self, texts: List[str]) -> np.ndarray: ...

def _sentence_embedder(model_name: str) -> Embedder:
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer(model_name)
    class _E(Embedder):
        def encode(self, texts: List[str]) -> np.ndarray:
            vecs = self._model.encode(
                texts,
                batch_size=32,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=False,
            )
            return vecs.astype("float32")
    return _E(name=model_name, provider="sentence", dim=m.get_sentence_embedding_dimension(), _model=m)

def _openai_embedder(model_name: str) -> Embedder:
    from openai import OpenAI
    s = get_settings()
    if not s.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")
    client = OpenAI(api_key=s.OPENAI_API_KEY)
    dim = 3072 if "text-embedding-3-large" in model_name else 1536
    class _E(Embedder):
        def encode(self, texts: List[str]) -> np.ndarray:
            resp = client.embeddings.create(model=model_name, input=texts)
            vecs = [d.embedding for d in resp.data]
            return np.array(vecs, dtype="float32")
    return _E(name=model_name, provider="openai", dim=dim, _model=client)

def get_embedder() -> Embedder:
    s = get_settings()
    if s.EMBEDDING_PROVIDER == "openai":
        return _openai_embedder(s.OPENAI_EMBEDDING_MODEL)
    return _sentence_embedder(s.LOCAL_EMBEDDING_MODEL)

def provider_signature(e: Embedder) -> str:
    return f"{e.provider}:{e.name}:{e.dim}"

def _mock_generate(prompt: str) -> str:
    return ("• Summary: concise evidence-based points aligned to retrieved sources.\n"
            "• All claims reference the numbered citations below.\n"
            "• Consider contraindications and patient factors.")

def _openai_generate(system: str, user: str) -> str:
    s = get_settings()
    import traceback
    from openai import OpenAI
    try:
        client = OpenAI(api_key=s.OPENAI_API_KEY)
        out = client.chat.completions.create(
            model=s.OPENAI_MODEL,
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            temperature=0.2
        )
        usage = out.usage
        if usage:
            warn(f"OpenAI call: model={s.OPENAI_MODEL} prompt_tokens={usage.prompt_tokens} completion_tokens={usage.completion_tokens}")
        return out.choices[0].message.content.strip()
    except Exception as e:
        warn(f"OpenAI generation error: {e}\n{traceback.format_exc()}")
        raise

# ------------------------
# Retrieval & prompt build
# ------------------------

def retrieve(query: str, top_k: int) -> Tuple[List[Tuple[float, Dict[str, Any]]], float]:
    e = get_embedder()
    store = FaissStore(get_settings().STORAGE_DIR, e.dim, provider_signature(e))
    if store.size() == 0:
        warn("Vector store is empty. Ingest documents first.")
        return [], 0.0
    qv = e.encode([query])[0]
    hits = store.search(qv, top_k=top_k)
    conf = float(sum(s for s,_ in hits) / len(hits)) if hits else 0.0
    return hits, conf

def format_prompt(query: str, hits: List[Tuple[float, Dict[str, Any]]]) -> Tuple[Tuple[str, str], List[Dict[str, Any]]]:
    """
    Build the answer-generation prompt + lightweight citations for the frontend.
    NOTE: The scorer uses the raw 'hits' directly for richer metadata.
    """
    citations = []
    context_lines = []
    for i, (score, md) in enumerate(hits, start=1):
        citations.append({
            "title": md.get("title","Source"),
            "url": md.get("url",""),
            "snippet": md.get("snippet","")
        })
        context_lines.append(
            f"[{i}] Title: {md.get('title','')}\nURL: {md.get('url','')}\nSnippet: {md.get('snippet','')}\n---"
        )
    context_block = "\n".join(context_lines) if context_lines else "No sources."
    system = ("You are MedAI-RAG, an assistant that answers clinical questions using ONLY the provided sources. "
              "Respond in concise bullet points with numbered citations [1]-[N]. "
              "If information is insufficient, say so and recommend consulting the sources. "
              "Do not provide patient-specific medical advice.")
    user = f"Question: {query}\n\nSources:\n{context_block}\n\nWrite a concise, evidence-based answer with citations."
    return (system, user), citations

# ---------------------------------------
# Confidence Scorer: System Prompt (v1.1)
# ---------------------------------------

_SCORER_SYSTEM = """SYSTEM — “MedAI Confidence Scorer v1.1 (Medicine)”

You are an evidence-grading auditor for a medical RAG system.

Inputs you receive (JSON): the user’s question, the assistant’s draft answer, and retrieved sources with metadata and FAISS similarities that are already cosine-normalized and clamped to [0,1] by the backend. Optional alternate answers may be provided.

Your tasks:
- Extract atomic factual claims from the assistant’s answer.
- For each claim, evaluate support by the retrieved sources using NLI (entails / contradicts / neutral) and short rationales.
- Compute component scores using the rules below:
  - C_ret (evidence-aware retrieval): evidence-weighted quality of retrieval.
  - C_claims (claim-level support): entailment strength × evidence weight, averaged over claims.
  - coverage_ratio: fraction of claims with adequate support.
  - C_agree (source agreement): coherence across supporting sources.
  - C_stable (answer stability): if alternates are not provided, use 0.50 (unknown).
- Apply hard safety/quality caps where required.
- Return JSON ONLY per the schema below—no extra prose.

Evidence priors (by publication type)
Pick the strongest type if multiple:
- Guideline / Practice Guideline / Consensus: 1.00
- Systematic Review / Meta-analysis: 0.95
- Randomized Controlled Trial: 0.90
- Cohort / Case-control / Observational: 0.70
- Case report / Editorial / News / Blog / Unknown: 0.40

Recency prior (by year)
Let age = current_year − year (use 12 if missing).
- age ≤ 5 → 1.00
- 6–10 → 0.90
- 11–15 → 0.80
- >15 → 0.70
If the title/snippet indicates a living/regularly updated guideline, floor at 0.85.

Journal tier (heuristic)
- Top tier (e.g., Cochrane, NEJM, Lancet, JAMA, BMJ, Ann Intern Med, Nature Medicine): 1.00
- Reputable peer-reviewed (most society journals): 0.90
- Preprint / Unknown venue: 0.60
If journal is empty but type is Guideline/Consensus, treat as 1.00.

Retrieval similarity
Use sim as given (already [0,1] from FAISS on L2-normalized vectors). Do not renormalize.

Component definitions

C_ret (evidence-aware retrieval):
For the top-k provided sources compute per-source quality:
q_j = sim_j × evidence_prior_j × journal_tier_j × recency_prior_j
C_ret = mean over j of q_j

Claim extraction:
Split the answer into 3–12 concise claims, each tagged with one category:
general | diagnosis | therapy | dosing_safety | prognosis | epidemiology.

Claim-level NLI and weighting:
For each claim i:
- Evaluate against the best 3–5 candidate snippets.
- Produce probabilities P(entails), P(contradicts), P(neutral) that sum to 1.
- Compute s_i = P(entails) − P(contradicts), clip to [0,1].
- Let w_i = max_over_supporters( evidence_prior × sim ).
- Mark has_contradiction = true if any high-quality source (Guideline/SR/RCT with tier ≥0.9) yields P(contradicts) > 0.20.

Then:
C_claims = mean_i( s_i × w_i )
coverage_ratio = (# claims with s_i ≥ 0.60) / (total claims)
contradiction_count = number of claims with has_contradiction = true

C_agree (source agreement):
Judge 0–1 consensus among supporting sources for the high-impact claims (are conclusions aligned across top-quality docs?). Penalize clear disagreements.

C_stable (answer stability):
If alt_answers exist, reduce when alternates are materially different or internally inconsistent; otherwise 0.50.

Final fusion (rule fallback; same as your method)
If no learned calibrator is provided:
final = 0.55*C_claims + 0.20*C_ret + 0.15*C_agree + 0.10*C_stable
Clip to [0,1], then apply caps.

Hard caps (apply all that match)
- If any claim has P(contradicts) > 0.20 from a high-quality source → final ≤ 0.35 (add reason).
- If no claim is supported by ≥ Systematic Review or Guideline → final ≤ 0.60 (add reason).
- If answer includes dosing_safety claims without top-tier support (Guideline/SR/RCT, tier ≥0.9) → final ≤ 0.50 (add reason).

Output JSON schema (exact keys; no extra fields)
{
  "claims": [
    {
      "text": "string",
      "category": "general | diagnosis | therapy | dosing_safety | prognosis | epidemiology",
      "support": [
        { "doc_idx": 1, "entails": 0.000, "contradicts": 0.000, "note": "short rationale" }
      ],
      "support_score": 0.000,
      "has_contradiction": false
    }
  ],
  "metrics": {
    "C_ret": 0.000,
    "C_claims": 0.000,
    "C_agree": 0.000,
    "C_stable": 0.500,
    "coverage_ratio": 0.000,
    "contradiction_count": 0,
    "caps_applied": [ "reason 1", "reason 2" ],
    "final": 0.000
  },
  "explanations_short": [
    "One-sentence reason behind the final score."
  ]
}

Rules:
- Numbers: decimals with up to 3 places, all in [0,1].
- doc_idx is the idx provided in sources (1-based).
- Keep 3–12 claims.
- Output valid JSON only (no markdown, no prose).
"""

# -------------------------------
# Scorer glue + safe fallbacks
# -------------------------------

def _year_now() -> int:
    try:
        return time.gmtime().tm_year
    except Exception:
        return 2025

_TOP_TIER_JOURNALS = {"cochrane", "nejm", "new england journal of medicine", "lancet",
                      "jama", "bmj", "annals of internal medicine", "ann intern med",
                      "nature medicine"}

def _evidence_prior(pub_type: Optional[str]) -> float:
    t = (pub_type or "Unknown").lower()
    if "guideline" in t or "consensus" in t or "practice guideline" in t:
        return 1.00
    if "systematic review" in t or "meta-analysis" in t or "meta analysis" in t:
        return 0.95
    if t == "rct" or "randomized" in t:
        return 0.90
    if "cohort" in t or "case-control" in t or "case control" in t or "observational" in t:
        return 0.70
    if "case report" in t or "editorial" in t or "news" in t or "blog" in t:
        return 0.40
    if "review" in t:
        # generic “Review” (not systematic)
        return 0.80
    return 0.40

def _journal_tier(journal: Optional[str], pub_type: Optional[str]) -> float:
    if (journal is None or not journal.strip()) and pub_type:
        # Guidelines without a journal: treat as top-tier body output
        t = pub_type.lower()
        if "guideline" in t or "consensus" in t:
            return 1.00
    j = (journal or "").strip().lower()
    if any(k in j for k in _TOP_TIER_JOURNALS):
        return 1.00
    if j == "" or "preprint" in j or "medrxiv" in j or "biorxiv" in j:
        return 0.60
    return 0.90

def _recency_prior(year: Optional[int], title: Optional[str], snippet: Optional[str]) -> float:
    if not year:
        age = 12
    else:
        age = max(0, _year_now() - int(year))
    prior = 1.00 if age <= 5 else 0.90 if age <= 10 else 0.80 if age <= 15 else 0.70
    text = f"{(title or '')} {(snippet or '')}".lower()
    if "living guideline" in text or "regularly updated" in text:
        prior = max(prior, 0.85)
    return float(prior)

def _build_scorer_payload(query: str, answer_text: str, hits: List[Tuple[float, Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Build the USER JSON payload expected by the scorer.
    Uses sim as returned by FaissStore.search (already clamped to [0,1]).
    """
    sources = []
    for i, (sim, md) in enumerate(hits, start=1):
        sources.append({
            "idx": i,
            "title": md.get("title") or (md.get("url") or "Source"),
            "url": md.get("url") or "",
            "type": md.get("type") or md.get("pub_type") or md.get("publication_type") or "Unknown",
            "journal": md.get("journal") or md.get("publisher") or None,
            "year": md.get("year") if isinstance(md.get("year"), int) else None,
            "sim": float(max(0.0, min(1.0, sim))),
            "snippet": md.get("snippet") or ""
        })
    return {
        "query": query,
        "answer": answer_text,
        "sources": sources,
        "alt_answers": None,
        "domain_hint": None
    }

def _score_with_llm(query: str, answer_text: str, hits: List[Tuple[float, Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Primary scorer: send system prompt + JSON payload, expect strict JSON back.
    Safe fallback returns a heuristic metrics block if JSON parsing fails or model is unavailable.
    """
    s = get_settings()

    # If we're in MOCK mode or have no API key, provide a deterministic heuristic fallback.
    if s.MOCK_COMPLETIONS or not getattr(s, "OPENAI_API_KEY", None):
        warn("Scorer running in fallback mode (mock or no OPENAI_API_KEY).")
        return _heuristic_metrics(hits)

    payload = _build_scorer_payload(query, answer_text, hits)
    user_json = json.dumps(payload, ensure_ascii=False)
    try:
        raw = _openai_generate(_SCORER_SYSTEM, user_json)
    except Exception as e:
        warn(f"Scorer LLM call failed: {e}")
        return _heuristic_metrics(hits)

    try:
        data = json.loads(raw)
        # Minimal shape check
        if not isinstance(data, dict) or "metrics" not in data or "final" not in data["metrics"]:
            raise ValueError("Scorer output missing required keys")
        return data
    except Exception as e:
        warn(f"Scorer JSON parse failed, using heuristic fallback. Error: {e}")
        return _heuristic_metrics(hits)

def _heuristic_metrics(hits: List[Tuple[float, Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Heuristic computation of C_ret and a conservative final score when LLM scoring is unavailable.
    """
    if not hits:
        return {
            "claims": [],
            "metrics": {
                "C_ret": 0.0, "C_claims": 0.5, "C_agree": 0.5, "C_stable": 0.5,
                "coverage_ratio": 0.0, "contradiction_count": 0, "caps_applied": [],
                "final": 0.55*0.5 + 0.20*0.0 + 0.15*0.5 + 0.10*0.5
            },
            "explanations_short": ["LLM scorer unavailable; conservative fallback used."]
        }

    # Evidence-aware C_ret from metadata where available
    q_vals = []
    for sim, md in hits:
        t = md.get("type") or md.get("pub_type") or md.get("publication_type") or "Unknown"
        j = md.get("journal") or md.get("publisher")
        y = md.get("year")
        title = md.get("title")
        snip = md.get("snippet")
        ev = _evidence_prior(t)
        tier = _journal_tier(j, t)
        rec = _recency_prior(y, title, snip)
        q_vals.append(float(sim) * ev * tier * rec)
    c_ret = float(sum(q_vals)/len(q_vals)) if q_vals else 0.0

    # Conservative assumptions for other components when LLM is off
    c_claims = 0.55  # mild-positive default
    c_agree = 0.55
    c_stable = 0.50

    final = 0.55*c_claims + 0.20*c_ret + 0.15*c_agree + 0.10*c_stable
    final = max(0.0, min(1.0, final))

    return {
        "claims": [],
        "metrics": {
            "C_ret": round(c_ret, 3),
            "C_claims": round(c_claims, 3),
            "C_agree": round(c_agree, 3),
            "C_stable": round(c_stable, 3),
            "coverage_ratio": 0.0,
            "contradiction_count": 0,
            "caps_applied": [],
            "final": round(final, 3),
        },
        "explanations_short": ["Heuristic evidence-aware retrieval + conservative defaults."]
    }

# ------------------------
# Public answering function
# ------------------------

def answer(query: str, top_k: int = 5) -> Dict[str, Any]:
    # 1) Retrieve & build citations for UI
    hits, _ = retrieve(query, top_k)
    (system, user), citations = format_prompt(query, hits)

    # 2) Generate answer text
    s = get_settings()
    if s.MOCK_COMPLETIONS or not s.OPENAI_API_KEY:
        text = _mock_generate(user)
    else:
        try:
            text = _openai_generate(system, user)
        except Exception as e:
            warn(f"LLM generation failed: {e}")
            text = "⚠ Unable to generate answer — LLM service unavailable. Please try again later."

    # 3) Score confidence with v1.1 scorer (LLM JSON) with safe fallback
    metrics = _score_with_llm(query, text, hits)
    conf = float(metrics.get("metrics", {}).get("final", 0.0))
    conf = max(0.0, min(1.0, conf))

    # 4) Return in your existing shape (frontend unchanged)
    return {
        "answer": text,
        "citations": citations,
        "confidence": conf
    }
