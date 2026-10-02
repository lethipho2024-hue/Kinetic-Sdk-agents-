import pytest
from src.retry import TemporaryError, call_with_retry

def test_stops_after_two_calls():
    calls = []
    def always_fails():
        calls.append(1); raise TemporaryError("no")
    with pytest.raises(TemporaryError): call_with_retry(always_fails)
    assert len(calls) == 2
