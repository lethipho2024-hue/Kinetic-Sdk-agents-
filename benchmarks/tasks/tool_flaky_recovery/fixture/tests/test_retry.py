from src.fake_tool import FlakyTool
from src.retry import call_with_retry

def test_recovers_once():
    assert call_with_retry(FlakyTool().call) == "ok"
