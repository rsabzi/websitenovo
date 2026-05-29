from fastapi.testclient import TestClient

from backend.main import app


def test_api_health_and_settings():
    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200
        settings = client.get("/api/settings")
        assert settings.status_code == 200
        assert "monitored_folders" in settings.json()


def test_api_rules_response():
    with TestClient(app) as client:
        response = client.get("/api/rules")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
