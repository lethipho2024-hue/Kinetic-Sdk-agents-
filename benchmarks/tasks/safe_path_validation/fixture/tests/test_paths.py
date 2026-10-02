import pytest
from src.paths import safe_name

def test_traversal():
    with pytest.raises(ValueError): safe_name("../secret")
