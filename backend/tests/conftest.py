"""Shared test fixtures for MedAI-RAG backend tests."""

from unittest.mock import patch, MagicMock

import pytest
from starlette.testclient import TestClient

from app.config import Settings, get_settings


# ---------------------------------------------------------------------------
# mock_settings — patched Settings with safe defaults for testing
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_settings(tmp_path, monkeypatch):
    """Return a Settings object that never hits real APIs.

    * MOCK_COMPLETIONS = True  (skip OpenAI calls)
    * OPENAI_API_KEY  = ""     (lifespan skips key validation)
    * STORAGE_DIR     = <tmp_path>/storage  (isolated per-test)
    * Clears the lru_cache on get_settings so the patched version is used.
    * Resets module-level caches in app.rag.
    """
    storage = tmp_path / "storage"
    storage.mkdir()

    test_settings = Settings.__new__(Settings)
    test_settings.HOST = "0.0.0.0"
    test_settings.PORT = 8000
    test_settings.CORS_ORIGINS = ["http://localhost:5173"]
    test_settings.STORAGE_DIR = str(storage)
    test_settings.EMBEDDING_PROVIDER = "sentence"
    test_settings.LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    test_settings.OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
    test_settings.OPENAI_API_KEY = ""
    test_settings.OPENAI_MODEL = "gpt-4o-mini"
    test_settings.MOCK_COMPLETIONS = True

    # Clear the lru_cache so our patched factory is used everywhere.
    get_settings.cache_clear()

    _gs = lambda: test_settings
    monkeypatch.setattr("app.config.get_settings", _gs)

    # Patch every module that did `from .config import get_settings` — they
    # hold their own reference to the original function.
    monkeypatch.setattr("app.rag.get_settings", _gs)
    monkeypatch.setattr("app.ingest.get_settings", _gs)
    monkeypatch.setattr("app.query_suggest.get_settings", _gs)

    # Also patch the already-imported reference in main (module-level `s`).
    monkeypatch.setattr("app.main.s", test_settings)

    # Reset cached singletons in app.rag so tests get fresh instances.
    import app.rag as rag_mod
    monkeypatch.setattr(rag_mod, "_embedder_cache", None)
    monkeypatch.setattr(rag_mod, "_store_cache", None)

    yield test_settings

    # Post-test: clear lru_cache again so other tests/sessions start clean.
    get_settings.cache_clear()


# ---------------------------------------------------------------------------
# mock_firebase_auth — bypass Firebase token verification
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_firebase_auth():
    """Patch firebase_admin.auth.verify_id_token to return a fake decoded token."""
    fake_decoded = {"uid": "test-user-123"}
    with patch("firebase_admin.auth.verify_id_token", return_value=fake_decoded) as mock_verify:
        yield mock_verify


# ---------------------------------------------------------------------------
# test_client — FastAPI TestClient with mocked settings + firebase
# ---------------------------------------------------------------------------

@pytest.fixture()
def test_client(mock_settings, mock_firebase_auth):
    """Provide a Starlette TestClient wired to the FastAPI app.

    Depends on mock_settings (safe config) and mock_firebase_auth (no real
    Firebase calls) so every request through this client is fully isolated.
    """
    from app.main import app

    with TestClient(app) as client:
        yield client


# ---------------------------------------------------------------------------
# tmp_storage — lightweight fixture when you only need a temp directory
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_storage(tmp_path):
    """Return a temporary storage directory path (pathlib.Path)."""
    storage = tmp_path / "storage"
    storage.mkdir()
    return storage
