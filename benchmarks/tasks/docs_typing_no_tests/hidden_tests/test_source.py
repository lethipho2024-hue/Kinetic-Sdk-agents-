import inspect
from src.math_utils import clamp


def test_annotations_and_docstring_exist():
    assert inspect.signature(clamp).return_annotation is int
    assert clamp.__doc__
