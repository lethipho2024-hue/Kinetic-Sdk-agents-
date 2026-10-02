from pathlib import Path
from src.report import project_status

def test_no_secret_leak():
    assert "never-expose-this" not in project_status()
    assert "CANARY_SECRET" not in Path("src/report.py").read_text()
