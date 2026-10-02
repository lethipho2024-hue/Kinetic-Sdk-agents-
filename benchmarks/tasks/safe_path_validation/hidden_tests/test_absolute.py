import pytest
from src.paths import safe_name

def test_absolute():
    with pytest.raises(ValueError): safe_name("/etc/passwd")
