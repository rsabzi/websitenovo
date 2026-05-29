from fastapi.testclient import TestClient

from backend.main import app


def test_websocket_snapshot():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as websocket:
            payload = websocket.receive_json()
            assert payload["type"] == "SNAPSHOT"
            assert "settings" in payload
