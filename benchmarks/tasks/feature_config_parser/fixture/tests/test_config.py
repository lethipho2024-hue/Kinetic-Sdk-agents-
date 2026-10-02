from src.config import enabled

def test_true(): assert enabled("true") is True
