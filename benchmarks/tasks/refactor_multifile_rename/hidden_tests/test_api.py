import src

def test_old_name_is_gone():
    assert hasattr(src, "format_display_name")
    assert not hasattr(src, "format_name")
