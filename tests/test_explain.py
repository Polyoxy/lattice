from dataclasses import replace

from lattice.harmony.functions import build_function
from lattice.harmony.grammar import Loop
from lattice.section import SectionRender
from lattice.theory.key import parse_key
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


def test_explain_labels_loop_a_and_loop_b_when_section_b_present() -> None:
    key = parse_key("Am")
    b_loop = Loop(key, (build_function(key, "iv7"),), bars=4)
    sr = SectionRender(loop=b_loop, segments=(), voicings=(), parts_a={}, parts_b={})
    b = replace(_beat(), section_b=sr)
    text = b.explain()
    assert "loop A: Am9 (i9) → Fmaj7 (bVImaj7)" in text
    assert "loop B: Dm7 (iv7)" in text
    assert "loop: " not in text
