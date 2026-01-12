import json
import pytest
from src.App import *

@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_index_get(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<html" in resp.data


def test_api_chat_missing_message(client):
    resp = client.post("/api/chat", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_api_chat_normal_message(client):
    resp = client.post("/api/chat", json={"message": "hello"})
    data = resp.get_json()
    assert resp.status_code == 200
    assert "reply" in data
    assert data["type"] in {"chat", "gratitude"}


def test_moodlog_post_and_get(client, tmp_path, monkeypatch):
    # Override file locations to temp files
    mood_file = tmp_path / "mood.json"
    mood_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr("src.App.MOOD_FILE", str(mood_file))

    new_entry = {"date": "2025-01-01", "mood": "Happy", "note": "Feeling great"}
    resp = client.post("/api/moodlog", json=new_entry)
    assert resp.status_code == 201

    resp = client.get("/api/moodlog")
    data = resp.get_json()
    assert isinstance(data, list)
    assert data[-1]["mood"] == "Happy"


def test_404_handler(client):
    resp = client.get("/nonexistent")
    assert resp.status_code == 404
    assert "error" in resp.get_json()
