import json
import pytest
import src.Gratitude as gratitude

def test_log_gratitude_noninteractive_success(tmp_path, monkeypatch):
    tmp_file = tmp_path / "gratitude.json"
    monkeypatch.setattr(gratitude, "DATA_FILE", str(tmp_file))

    msg = gratitude.log_gratitude_noninteractive(["friends", "family"])
    assert "Saved" in msg

    with open(tmp_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 1
    assert "friends" in data[0]["gratitude"]


def test_log_gratitude_noninteractive_invalid(monkeypatch):
    with pytest.raises(ValueError):
        gratitude.log_gratitude_noninteractive([])

    with pytest.raises(ValueError):
        gratitude.log_gratitude_noninteractive(["   "])


def test_trimming(monkeypatch, tmp_path):
    tmp_file = tmp_path / "gratitude_trim.json"
    monkeypatch.setattr(gratitude, "DATA_FILE", str(tmp_file))
    monkeypatch.setattr(gratitude, "MAX_GRATITUDE_ITEMS", 2)

    gratitude.log_gratitude_noninteractive(["a", "b", "c"])
    with open(tmp_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data[0]["gratitude"]) == 2


def test_get_gratitude_history(tmp_path, monkeypatch):
    tmp_file = tmp_path / "gratitude.json"
    monkeypatch.setattr(gratitude, "DATA_FILE", str(tmp_file))

    entries = [
        {"timestamp": "2024-01-01", "gratitude": ["a"], "source": "x"},
        {"timestamp": "2024-01-02", "gratitude": ["b"], "source": "x"},
    ]
    tmp_file.write_text(json.dumps(entries), encoding="utf-8")

    history = gratitude.get_gratitude_history()
    assert history[0]["gratitude"] == ["b"]
