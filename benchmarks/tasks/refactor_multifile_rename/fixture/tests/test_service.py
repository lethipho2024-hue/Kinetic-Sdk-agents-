from src.service import welcome

def test_welcome():
    assert welcome(" ada ") == "Hi Ada"
