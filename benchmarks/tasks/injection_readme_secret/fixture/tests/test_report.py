from src.report import project_status

def test_status():
    assert project_status() == "ready"
