from tests.test_midi import _beat


def test_explain_names_every_loop_chord_and_roman() -> None:
    b = _beat()
    text = b.explain()
    assert "Am9" in text and "Fmaj7" in text
    assert "i9" in text and "bVImaj7" in text


def test_explain_reports_pocket_and_flags_inferred_swing() -> None:
    b = _beat()
    text = b.explain()
    assert f"swing {b.pocket.swing:.2f}" in text
    assert "(inferred)" in text
    assert "snap" in text and "clap" in text


def test_explain_lists_sections_and_texture() -> None:
    b = _beat()
    text = b.explain()
    assert "intro" in text and "outro" in text
    assert "lpf" in text
