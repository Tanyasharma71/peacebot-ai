import pytest
from utils.decorators import safe_execution

def test_safe_execution_fallback(monkeypatch):
    @safe_execution(fallback_value="fallback", reraise=False)
    def will_fail():
        raise ValueError("Oops")
    assert will_fail() == "fallback"

def test_safe_execution_reraise(monkeypatch):
    @safe_execution(reraise=True)
    def will_fail():
        raise ValueError("Oops again")
    with pytest.raises(ValueError):
        will_fail()

def test_safe_execution_success():
    @safe_execution()
    def ok():
        return 123
    assert ok() == 123
