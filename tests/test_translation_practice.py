from handlers.translation_practice import normalize_text


def test_normalize_text():
    assert normalize_text("  Hamkorlik  ") == "hamkorlik"
    assert normalize_text("partnership!") == "partnership"
    assert normalize_text("  o'zaro manfaat  ") == "ozaro manfaat"
