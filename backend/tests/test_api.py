"""Integration tests for FastAPI backend endpoints.

Uses TestClient with MOCK_COMPLETIONS=True via the fixtures in conftest.py.
"""

import io

import pytest

AUTH_HEADER = {"Authorization": "Bearer test-token"}


# ---------------------------------------------------------------------------
# 1. GET /health
# ---------------------------------------------------------------------------

def test_health_returns_200_with_expected_fields(test_client):
    resp = test_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert "store_loaded" in data
    assert "embedding_ready" in data
    assert "doc_count" in data
    assert "embedding_provider" in data


# ---------------------------------------------------------------------------
# 2. POST /ask with empty store
# ---------------------------------------------------------------------------

def test_ask_empty_store(test_client):
    resp = test_client.post("/ask", json={"query": "What is aspirin?", "top_k": 5}, headers=AUTH_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "citations" in data
    assert "confidence" in data
    assert isinstance(data["confidence"], float)
    assert 0 <= data["confidence"] <= 1


# ---------------------------------------------------------------------------
# 3. POST /ask with top_k > 50
# ---------------------------------------------------------------------------

def test_ask_top_k_too_large(test_client):
    resp = test_client.post("/ask", json={"query": "test query", "top_k": 100}, headers=AUTH_HEADER)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 4. POST /ask with query too short
# ---------------------------------------------------------------------------

def test_ask_query_too_short(test_client):
    resp = test_client.post("/ask", json={"query": "x", "top_k": 5}, headers=AUTH_HEADER)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 5. POST /ask with query too long
# ---------------------------------------------------------------------------

def test_ask_query_too_long(test_client):
    long_query = "a" * 2001
    resp = test_client.post("/ask", json={"query": long_query, "top_k": 5}, headers=AUTH_HEADER)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 6. POST /ingest rejects without auth
# ---------------------------------------------------------------------------

def test_ingest_rejects_without_auth(test_client):
    files = [("files", ("test.txt", io.BytesIO(b"Some content here."), "text/plain"))]
    resp = test_client.post("/ingest", files=files)
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 7. POST /ingest with auth adds documents
# ---------------------------------------------------------------------------

def test_ingest_with_auth_adds_documents(test_client):
    content = b"Title: Test Doc\nURL: http://test.com\n\nThis is test content for ingestion. " * 20
    files = [("files", ("test.txt", io.BytesIO(content), "text/plain"))]
    resp = test_client.post("/ingest", files=files, headers=AUTH_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["added"] > 0


# ---------------------------------------------------------------------------
# 8. GET /documents returns ingested docs
# ---------------------------------------------------------------------------

def test_documents_returns_ingested_docs(test_client):
    # First ingest a document
    content = b"Title: Test Doc\nURL: http://test.com\n\nThis is test content for ingestion. " * 20
    files = [("files", ("test.txt", io.BytesIO(content), "text/plain"))]
    resp = test_client.post("/ingest", files=files, headers=AUTH_HEADER)
    assert resp.status_code == 200

    # Then list documents with the same auth
    resp = test_client.get("/documents", headers=AUTH_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] > 0
    assert len(data["docs"]) > 0


# ---------------------------------------------------------------------------
# 9. GET /documents scoping (guest cannot see user-scoped docs)
# ---------------------------------------------------------------------------

def test_documents_scoping_guest_cannot_see_user_docs(test_client):
    # Ingest a document as authenticated user
    content = b"Title: Scoped Doc\nURL: http://scoped.com\n\nThis is scoped test content. " * 20
    files = [("files", ("scoped.txt", io.BytesIO(content), "text/plain"))]
    resp = test_client.post("/ingest", files=files, headers=AUTH_HEADER)
    assert resp.status_code == 200
    assert resp.json()["added"] > 0

    # Query as guest (no auth header) -- should not see user-scoped docs
    resp = test_client.get("/documents")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 0


# ---------------------------------------------------------------------------
# 10. POST /suggest-terms
# ---------------------------------------------------------------------------

def test_suggest_terms(test_client):
    resp = test_client.post(
        "/suggest-terms",
        json={"message": "What are the effects of metformin on diabetes?"},
        headers=AUTH_HEADER,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "terms" in data
    assert isinstance(data["terms"], list)
    assert "intent" in data
    assert isinstance(data["intent"], str)
    assert "method" in data
    assert isinstance(data["method"], str)
