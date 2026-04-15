"""Unit tests for app/vectorstore/faiss_store.py — FaissStore."""

import numpy as np
import pytest

from app.vectorstore.faiss_store import FaissStore


DIM = 8
SIG = "test:mock-model:8"


@pytest.fixture()
def store(tmp_path):
    """Create a FaissStore in a temp directory."""
    return FaissStore(storage_dir=str(tmp_path / "vs"), dim=DIM, provider_signature=SIG)


def _random_vecs(n: int, dim: int = DIM) -> np.ndarray:
    rng = np.random.default_rng(42)
    return rng.standard_normal((n, dim)).astype("float32")


# ---------------------------------------------------------------------------
# size() and add()
# ---------------------------------------------------------------------------

class TestAddAndSize:
    def test_empty_store_size_zero(self, store):
        assert store.size() == 0

    def test_add_increases_size(self, store):
        vecs = _random_vecs(5)
        metas = [{"doc": f"d{i}"} for i in range(5)]
        store.add(vecs, metas)
        assert store.size() == 5

    def test_add_multiple_batches(self, store):
        store.add(_random_vecs(3), [{"i": i} for i in range(3)])
        store.add(_random_vecs(2), [{"i": i} for i in range(2)])
        assert store.size() == 5


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------

class TestSearch:
    def test_results_ordered_by_descending_similarity(self, store):
        vecs = _random_vecs(10)
        metas = [{"idx": i} for i in range(10)]
        store.add(vecs, metas)

        query = _random_vecs(1)[0]
        results = store.search(query, top_k=5)
        scores = [s for s, _ in results]
        assert scores == sorted(scores, reverse=True)

    def test_scores_clamped_to_unit_interval(self, store):
        vecs = _random_vecs(10)
        metas = [{"idx": i} for i in range(10)]
        store.add(vecs, metas)

        query = _random_vecs(1)[0]
        results = store.search(query, top_k=10)
        for score, _ in results:
            assert 0.0 <= score <= 1.0

    def test_top_k_larger_than_store_size(self, store):
        vecs = _random_vecs(3)
        metas = [{"idx": i} for i in range(3)]
        store.add(vecs, metas)

        query = _random_vecs(1)[0]
        results = store.search(query, top_k=100)
        assert len(results) <= 3

    def test_empty_store_search_returns_empty(self, store):
        query = _random_vecs(1)[0]
        results = store.search(query, top_k=5)
        assert results == []

    def test_search_returns_correct_metadata(self, store):
        vecs = _random_vecs(3)
        metas = [{"title": f"doc_{i}"} for i in range(3)]
        store.add(vecs, metas)

        query = vecs[1]  # query with an exact vector we added
        results = store.search(query, top_k=1)
        assert len(results) == 1
        score, meta = results[0]
        # The closest match to vecs[1] should be doc_1
        assert meta["title"] == "doc_1"
        assert score == pytest.approx(1.0, abs=1e-4)


# ---------------------------------------------------------------------------
# _normalize()
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_output_unit_length(self):
        vecs = _random_vecs(5)
        normed = FaissStore._normalize(vecs)
        norms = np.linalg.norm(normed, axis=1)
        np.testing.assert_allclose(norms, 1.0, atol=1e-6)

    def test_zero_vector_handled(self):
        vecs = np.zeros((1, DIM), dtype="float32")
        normed = FaissStore._normalize(vecs)
        # Should not produce NaN/Inf thanks to epsilon
        assert np.all(np.isfinite(normed))


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

class TestPersistence:
    def test_metadata_and_vectors_survive_reload(self, tmp_path):
        storage = str(tmp_path / "persist")
        store1 = FaissStore(storage_dir=storage, dim=DIM, provider_signature=SIG)

        vecs = _random_vecs(4)
        metas = [{"name": f"item_{i}"} for i in range(4)]
        store1.add(vecs, metas)
        assert store1.size() == 4

        # Create a brand-new FaissStore pointing at the same directory
        store2 = FaissStore(storage_dir=storage, dim=DIM, provider_signature=SIG)
        assert store2.size() == 4

        # Verify metadata loaded correctly
        query = vecs[0]
        results = store2.search(query, top_k=1)
        assert len(results) == 1
        _, meta = results[0]
        assert meta["name"] == "item_0"
