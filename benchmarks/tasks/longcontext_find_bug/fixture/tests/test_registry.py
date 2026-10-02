from src.registry import label

def test_label():
    assert label("ready") == "ready!"
