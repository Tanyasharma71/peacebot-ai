import pytest
from src.App import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()

def test_health_llm_endpoint(client):
    """Ensure /healthz/llm returns valid fields and correct headers."""
    resp = client.get("/healthz/llm")
    data = resp.get_json()

    # JSON structure
    assert "status" in data
    assert "latency_ms" in data
    assert "model" in data
    assert "timestamp" in data

    # Header checks
    assert "X-Model-Version" in resp.headers
    assert "X-Latency-MS" in resp.headers

    # Status logic
    assert resp.status_code in (200, 503)
