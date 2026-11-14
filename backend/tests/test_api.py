import os
os.environ.setdefault("APP_ENV", "dev")
os.environ.setdefault("API_KEY", "test-key")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_public():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_clusters_requires_key():
    r = client.get("/clusters")
    assert r.status_code == 401


def test_investigate_requires_key():
    r = client.post("/investigate", json={})
    assert r.status_code == 401


def test_investigate_injection_422():
    r = client.post("/investigate", json={"namespace": "x; id"}, headers={"X-API-Key": "test-key"})
    assert r.status_code == 422
