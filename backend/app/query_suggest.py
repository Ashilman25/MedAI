import re, json
from typing import List, Tuple
from .config import get_settings
from .rag import _openai_generate

_STOP = set((
    "a an the of for with to in on from into across about how what which who whom whose "
    "why where when is are was were be been being do does did can could should would may "
    "might will shall and or not if then else than as by at over under between within"
).split())

_DOMAIN_HINTS = {
    "obesity","childhood obesity","pediatric obesity","anticoagulant","atrial fibrillation",
    "adverse effects","side effects","contraindication","hypertension","diabetes",
    "myocardial infarction","stroke","thrombosis","pulmonary embolism","heart failure",
    "long-term","complications","screening","diagnosis","management","therapy","treatment"
}

_INTENT_RULES = [
  (r"(side effect|adverse|toxici|contraindicat|risk|harm|safety)", "dosing_safety"),
  (r"(diagnos|screen|criteria|test|sensitivity|specificity|predict|rule[- ]?out)", "diagnosis"),
  (r"(treat|therapy|therapeutic|management|dose|dosing|regimen|guideline)", "therapy"),
  (r"(prognos|mortality|survival|recurrence|outcome)", "prognosis"),
  (r"(incidence|prevalence|epidemiolog)", "epidemiology"),
]

def _heuristic_terms(message: str, k: int = 6) -> List[str]:
    text = re.sub(r"[^a-zA-Z0-9\s\-]", " ", message).lower()
    toks = [t for t in text.split() if t and t not in _STOP]
    if not toks:
        return []

    grams = set()
    for i in range(len(toks)):
        grams.add(toks[i])
        if i + 1 < len(toks):
            grams.add(f"{toks[i]} {toks[i+1]}")
        if i + 2 < len(toks):
            grams.add(f"{toks[i]} {toks[i+1]} {toks[i+2]}")

    scored = []
    for g in grams:
        base = 1.0 + 0.1 * (len(g.split()) - 1)
        if g in _DOMAIN_HINTS:
            base *= 1.2
        scored.append((base, g))
    scored.sort(reverse=True)

    out, seen = [], set()
    for _, g in scored:
        key = g.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
        if len(out) >= k:
            break

    # light synonym enrichments
    if "childhood obesity" in out and "pediatric obesity" not in out:
        out.append("pediatric obesity")
    if "adverse effects" in out and "side effects" not in out:
        out.append("side effects")
    return out

def _heuristic_intent(message: str) -> str:
    m = message.lower()
    for pat, lab in _INTENT_RULES:
        if re.search(pat, m):
            return lab
    return "general"

def extract_terms_and_intent(message: str) -> Tuple[List[str], str, str]:
    s = get_settings()
    terms = _heuristic_terms(message, k=int(getattr(s, "SUGGEST_TERMS_MAX", 6)))
    intent = _heuristic_intent(message)
    method = "heuristic"

    # Optional LLM override/merge
    if getattr(s, "OPENAI_API_KEY", None) and str(getattr(s, "SUGGEST_TERMS_USE_LLM", "true")).lower() == "true":
        system = (
            "Extract 3-8 PubMed search terms (short noun phrases ≤3 words, no filler) "
            "and classify the question intent as one of: general | diagnosis | therapy | "
            "dosing_safety | prognosis | epidemiology. Return STRICT JSON: "
            '{"terms": ["..."], "intent": "dosing_safety"}'
        )
        user = f"Text: {message}"
        try:
            raw = _openai_generate(system, user)
            data = json.loads(raw)
            llm_terms = [t for t in data.get("terms", []) if isinstance(t, str)]
            llm_intent = data.get("intent") or intent
            merged, seen = [], set()
            for t in (llm_terms + terms):
                k = t.strip().lower()
                if k and k not in seen:
                    seen.add(k); merged.append(t.strip())
            terms = merged[: int(getattr(s, "SUGGEST_TERMS_MAX", 6))]
            intent = llm_intent
            method = "llm"
        except Exception:
            pass

    return terms, intent, method
