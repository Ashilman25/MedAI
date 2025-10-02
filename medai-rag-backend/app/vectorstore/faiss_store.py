import os, json
from typing import List, Tuple, Dict, Any
import numpy as np
from ..logging_config import warn
try:
    import faiss  # type: ignore
    HAVE_FAISS = True
except Exception:
    HAVE_FAISS = False
    warn("FAISS not available; falling back to NumPy search (slower).")

class FaissStore:
    def __init__(self, storage_dir: str, dim: int, provider_signature: str):
        self.storage_dir = storage_dir
        self.index_path = os.path.join(storage_dir, "index.faiss")
        self.meta_path = os.path.join(storage_dir, "meta.json")
        self.cfg_path = os.path.join(storage_dir, "store_config.json")
        self.dim = dim
        self.provider_signature = provider_signature
        self._index = None
        self._meta = []
        self._load()
    def _load(self):
        if os.path.exists(self.cfg_path):
            with open(self.cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if cfg.get("provider_signature") != self.provider_signature:
                raise RuntimeError("Embedding config changed vs existing store. Clear storage/ or keep config consistent.")
            self.dim = int(cfg["dim"])
        else:
            self._save_config()
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self._meta = json.load(f)
        else:
            self._meta = []
        if HAVE_FAISS and os.path.exists(self.index_path):
            self._index = faiss.read_index(self.index_path)
        elif HAVE_FAISS:
            self._index = faiss.IndexFlatIP(self.dim)
        else:
            self.npy_path = os.path.join(self.storage_dir, "vectors.npy")
            if os.path.exists(self.npy_path):
                self._vectors = np.load(self.npy_path)
            else:
                self._vectors = np.empty((0, self.dim), dtype="float32")
    def _save(self):
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self._meta, f, ensure_ascii=False, indent=2)
        if HAVE_FAISS:
            faiss.write_index(self._index, self.index_path)
        else:
            np.save(self.npy_path, self._vectors)
        self._save_config()
    def _save_config(self):
        cfg = {"dim": self.dim, "provider_signature": self.provider_signature}
        with open(self.cfg_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    @staticmethod
    def _normalize(vecs: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12
        return vecs / norms
    def add(self, embeddings: np.ndarray, metadatas: List[Dict[str, Any]]):
        assert embeddings.shape[1] == self.dim
        vecs = self._normalize(embeddings.astype("float32"))
        if HAVE_FAISS:
            self._index.add(vecs)
        else:
            self._vectors = np.vstack([self._vectors, vecs])
        start_id = len(self._meta)
        for i, md in enumerate(metadatas):
            md = dict(md); md["id"] = start_id + i; self._meta.append(md)
        self._save()
    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        q = self._normalize(query_vec.reshape(1, -1).astype("float32"))
        if HAVE_FAISS:
            scores, idxs = self._index.search(q, top_k); scores = scores[0]; idxs = idxs[0]
        else:
            sims = (self._vectors @ q.T).ravel()
            idxs = np.argsort(-sims)[:top_k]; scores = sims[idxs]
        results = []
        for s, i in zip(scores, idxs):
            if i < 0 or i >= len(self._meta): continue
            results.append((float(max(0.0, min(1.0, s))), self._meta[i]))
        return results
    def size(self) -> int:
        if HAVE_FAISS: return self._index.ntotal
        else: return 0 if not hasattr(self, "_vectors") else self._vectors.shape[0]
