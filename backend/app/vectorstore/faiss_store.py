import os, json, time
from typing import List, Tuple, Dict, Any
import numpy as np
from ..logging_config import logger
from contextlib import contextmanager

try:
    import faiss  # type: ignore
    HAVE_FAISS = True
except Exception:
    HAVE_FAISS = False
    logger.warning("FAISS not available; falling back to NumPy search (slower).")

try:
    import fcntl  # POSIX file locking
except Exception:
    fcntl = None

@contextmanager
def store_lock(lock_path: str):
    """
    Cross-process lock to serialize reads/writes of the vector store.
    POSIX: fcntl.flock; Fallback: naive lock file.
    """
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    if fcntl:
        f = open(lock_path, "w")
        try:
            fcntl.flock(f, fcntl.LOCK_EX)
            yield
        finally:
            try:
                fcntl.flock(f, fcntl.LOCK_UN)
            finally:
                f.close()
    else:
        # Naive fallback for non-POSIX envs
        spin = 0.05
        while True:
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                break
            except FileExistsError:
                time.sleep(spin)
        try:
            yield
        finally:
            try:
                os.remove(lock_path)
            except Exception:
                pass

class FaissStore:
    def __init__(self, storage_dir: str, dim: int, provider_signature: str):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

        self.index_path = os.path.join(storage_dir, "index.faiss")
        self.meta_path = os.path.join(storage_dir, "meta.json")
        self.cfg_path = os.path.join(storage_dir, "store_config.json")
        self.lock_path = os.path.join(storage_dir, ".store.lock")

        self.dim = dim
        self.provider_signature = provider_signature
        self._index = None
        self._meta: List[Dict[str, Any]] = []
        self._vectors = None  # only for NumPy fallback

        self._load()

    def _atomic_write_json(self, path: str, payload: Any):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def _atomic_write_bytes(self, src_tmp: str, dst_path: str):
        # When an API writes via a library (faiss), write to tmp, then replace
        os.replace(src_tmp, dst_path)

    def _save_config(self):
        cfg = {"dim": self.dim, "provider_signature": self.provider_signature}
        tmp = self.cfg_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.cfg_path)

    def _load(self):
        with store_lock(self.lock_path):
            # Config
            if os.path.exists(self.cfg_path):
                try:
                    with open(self.cfg_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    if cfg.get("provider_signature") != self.provider_signature:
                        raise RuntimeError(
                            "Embedding config changed vs existing store. "
                            "Clear storage/ or keep config consistent."
                        )
                    self.dim = int(cfg["dim"])
                except Exception as e:
                    logger.warning("Failed to read store_config.json (%s); starting fresh config.", e)
                    self._save_config()
            else:
                self._save_config()

            # Meta
            if os.path.exists(self.meta_path):
                try:
                    with open(self.meta_path, "r", encoding="utf-8") as f:
                        self._meta = json.load(f)
                except Exception as e:
                    logger.warning("Failed to read meta.json (%s); quarantining and starting fresh.", e)
                    try:
                        os.replace(self.meta_path, self.meta_path + f".corrupt.{int(time.time())}")
                    except Exception:
                        pass
                    self._meta = []
            else:
                self._meta = []

            # Index
            if HAVE_FAISS:
                if os.path.exists(self.index_path):
                    try:
                        self._index = faiss.read_index(self.index_path)
                    except Exception as e:
                        logger.warning("Failed to read FAISS index (%s); quarantining and starting new index.", e)
                        try:
                            os.replace(self.index_path, self.index_path + f".corrupt.{int(time.time())}")
                        except Exception:
                            pass
                        self._index = faiss.IndexFlatIP(self.dim)
                else:
                    self._index = faiss.IndexFlatIP(self.dim)
            else:
                self.npy_path = os.path.join(self.storage_dir, "vectors.npy")
                if os.path.exists(self.npy_path):
                    try:
                        self._vectors = np.load(self.npy_path)
                    except Exception as e:
                        logger.warning("Failed to read vectors.npy (%s); starting fresh.", e)
                        self._vectors = np.empty((0, self.dim), dtype="float32")
                else:
                    self._vectors = np.empty((0, self.dim), dtype="float32")

    def _save(self):
        with store_lock(self.lock_path):
            # meta
            self._atomic_write_json(self.meta_path, self._meta)
            # index / vectors
            if HAVE_FAISS:
                tmp_index = self.index_path + ".tmp"
                faiss.write_index(self._index, tmp_index)
                self._atomic_write_bytes(tmp_index, self.index_path)
            else:
                tmp_npy = self.npy_path + ".tmp"
                with open(tmp_npy, "wb") as f:
                    np.save(f, self._vectors)
                os.replace(tmp_npy, self.npy_path)
            # config
            self._save_config()

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
            md = dict(md)
            md["id"] = start_id + i
            self._meta.append(md)
        self._save()

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        q = self._normalize(query_vec.reshape(1, -1).astype("float32"))
        if HAVE_FAISS:
            scores, idxs = self._index.search(q, top_k)
            scores = scores[0]
            idxs = idxs[0]
        else:
            sims = (self._vectors @ q.T).ravel()
            idxs = np.argsort(-sims)[:top_k]
            scores = sims[idxs]
        results = []
        for s, i in zip(scores, idxs):
            if i < 0 or i >= len(self._meta):
                continue
            results.append((float(max(0.0, min(1.0, s))), self._meta[i]))
        return results

    def size(self) -> int:
        if HAVE_FAISS:
            return int(self._index.ntotal)
        else:
            return 0 if self._vectors is None else int(self._vectors.shape[0])
