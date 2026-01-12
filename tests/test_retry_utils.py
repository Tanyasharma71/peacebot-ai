import time
import pytest
from utils.retry_utils import retry

counter = {"calls": 0}

@retry(max_retries=3, base_delay=0.1)
def unstable_func():
    counter["calls"] += 1
    if counter["calls"] < 3:
        raise ValueError("Fail!")
    return "success"

def test_retry_decorator_retries(monkeypatch):
    counter["calls"] = 0
    result = unstable_func()
    assert result == "success"
    assert counter["calls"] == 3

def test_retry_stops_after_max(monkeypatch):
    counter["calls"] = 0

    @retry(max_retries=2, base_delay=0.05)
    def always_fail():
        counter["calls"] += 1
        raise ValueError("Still broken")

    with pytest.raises(ValueError):
        always_fail()
    assert counter["calls"] == 2
