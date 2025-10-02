import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
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
            vecs = self._model.encode(texts, batch_size=32, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=False)
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
    return ("• Summary: concise evidence‑based points aligned to retrieved sources.\n"
            "• All claims reference the numbered citations below.\n"
            "• Consider contraindications and patient factors.")

def _openai_generate(system: str, user: str) -> str:
    s = get_settings()
    try:
        from openai import OpenAI
        client = OpenAI(api_key=s.OPENAI_API_KEY)
        out = client.chat.completions.create(
            model=s.OPENAI_MODEL,
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            temperature=0.2
        )
        return out.choices[0].message.content.strip()
    except Exception as e:
        warn(f"OpenAI generation error: {e}")
        return _mock_generate(user)

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

def format_prompt(query: str, hits: List[Tuple[float, Dict[str, Any]]]) -> Tuple[str, List[Dict[str, Any]]]:
    citations = []
    context_lines = []
    for i, (score, md) in enumerate(hits, start=1):
        citations.append({"title": md.get("title","Source"), "url": md.get("url",""), "snippet": md.get("snippet","")})
        context_lines.append(f"[{i}] Title: {md.get('title','')}\nURL: {md.get('url','')}\nSnippet: {md.get('snippet','')}\n---")
    context_block = "\n".join(context_lines) if context_lines else "No sources."
    system = ("You are MedAI‑RAG, an assistant that answers clinical questions using ONLY the provided sources. "
              "Respond in concise bullet points with numbered citations [1]‑[N]. "
              "If information is insufficient, say so and recommend consulting the sources. "
              "Do not provide patient‑specific medical advice.")
    user = f"Question: {query}\n\nSources:\n{context_block}\n\nWrite a concise, evidence‑based answer with citations."
    return (system, user), citations

def answer(query: str, top_k: int = 5) -> Dict[str, Any]:
    hits, conf = retrieve(query, top_k)
    (system, user), citations = format_prompt(query, hits)
    s = get_settings()
    if s.MOCK_COMPLETIONS or not s.OPENAI_API_KEY:
        text = _mock_generate(user)
    else:
        text = _openai_generate(system, user)
    return {"answer": text, "citations": citations, "confidence": max(0.0, min(1.0, conf))}
