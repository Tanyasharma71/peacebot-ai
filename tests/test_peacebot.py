import pytest
from src.peacebot import PeacebotResponder
from unittest.mock import MagicMock

def test_generate_with_openai_raises(monkeypatch, responder):
    # Force OpenAI mode
    responder._openai_available = True
    responder._sdk_mode = "new"

    # Proper mock client to avoid AttributeError
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("Forced failure")
    responder._client = mock_client

    with pytest.raises(Exception) as excinfo:
        responder._generate_with_openai("test prompt")

    assert "Forced failure" in str(excinfo.value)


@pytest.fixture
def responder():
    r = PeacebotResponder()
    # Ensure OpenAI is disabled for testing
    r._openai_available = False
    return r


def test_generate_response_empty_message(responder):
    result = responder.generate_response("")
    assert "I'm here with you" in result


@pytest.mark.parametrize("msg,expected_snippet", [
    ("I want to kill myself", "988"),
    ("I'm so anxious", "Anxiety"),
    ("I'm sad and lonely", "valid"),
    ("I'm angry today", "reset"),
    ("Just chilling", "listen")
])
def test_local_responses(responder, msg, expected_snippet):
    result = responder.generate_response(msg)
    assert expected_snippet.lower() in result.lower()

class DummyClient:
    class chat:
        class completions:
            @staticmethod
            def create(*args, **kwargs):
                raise Exception("dummy error")



def test_generate_with_openai_raises(monkeypatch, responder):
    # Force mode but break client
    responder._openai_available = True
    # responder._client = object()  # invalid client
    responder._client = DummyClient()
    responder._sdk_mode = "new"

    with pytest.raises(Exception):
        responder._generate_with_openai("test prompt")


def test_generate_locally_fallback(monkeypatch, responder):
    """Simulate exception inside local generation to trigger safe_execution fallback"""
    monkeypatch.setattr(responder, "CRISIS_MARKERS", None)  # cause exception
    result = responder._generate_locally("test message")
    assert "help" in result.lower()
