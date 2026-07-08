from handlers.translation_practice import add_missed_word, normalize_text


def test_normalize_text():
    assert normalize_text("  Hamkorlik  ") == "hamkorlik"
    assert normalize_text("partnership!") == "partnership"
    assert normalize_text("  o'zaro manfaat  ") == "ozaro manfaat"


def test_add_missed_word_deduplicates():
    existing = [{"word": "partnership", "translation": "hamkorlik"}]

    updated = add_missed_word(existing, {"word": "partnership", "translation": "hamkorlik"})
    assert len(updated) == 1

    updated = add_missed_word(existing, {"word": "collaboration", "translation": "hamkorlik"})
    assert len(updated) == 2
    assert updated[-1]["word"] == "collaboration"
