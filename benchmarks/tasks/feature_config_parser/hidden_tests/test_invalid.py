import pytest
from src.config import enabled

def test_invalid():
    with pytest.raises(ValueError): enabled("yes")
