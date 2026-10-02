from src.slug import slugify

def test_spaces():
    assert slugify("Hello World") == "hello-world"
