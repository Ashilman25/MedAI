"""Minimal smoke test to verify the test infrastructure works."""


def test_mock_settings_fixture(mock_settings):
    assert mock_settings.MOCK_COMPLETIONS is True
    assert mock_settings.OPENAI_API_KEY == ""
    assert "storage" in mock_settings.STORAGE_DIR


def test_test_client_health(test_client):
    resp = test_client.get("/health")
    assert resp.status_code == 200


def test_tmp_storage_fixture(tmp_storage):
    assert tmp_storage.exists()
    assert tmp_storage.is_dir()


def test_mock_firebase_auth_fixture(mock_firebase_auth):
    import firebase_admin.auth as fb_auth
    result = fb_auth.verify_id_token("fake-token")
    assert result["uid"] == "test-user-123"
