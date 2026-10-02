from src.slug import slugify

def test_surrounding_and_repeated_whitespace():
    assert slugify("  Hello   World  ") == "hello-world"
