from src.registry import label

def test_label_preserves_case():
    assert label("MiXeD") == "MiXeD!"
