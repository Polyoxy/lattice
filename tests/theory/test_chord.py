from lattice.theory.chord import build, chord_tpcs, is_dominant, symbol
from lattice.theory.pitch import parse_tpc, tpc_name


def test_m6add9_spelling_matches_rolling_stone_tab() -> None:
    em = build(parse_tpc("E"), "m6add9")
    assert [tpc_name(t) for t in chord_tpcs(em)] == ["E", "F#", "G", "B", "C#"]


def test_trust_loop_chords() -> None:
    assert symbol(build(parse_tpc("Db"), "maj7")) == "Dbmaj7"
    assert symbol(build(parse_tpc("F"), "m7")) == "Fm7"


def test_dominant_detection() -> None:
    assert is_dominant(build(parse_tpc("G"), "7b13"))
    assert is_dominant(build(parse_tpc("A"), "7"))
    assert not is_dominant(build(parse_tpc("E"), "m7"))
    assert not is_dominant(build(parse_tpc("C"), "maj7"))


def test_tritone_sub_guide_tone_arithmetic() -> None:
    g7 = build(parse_tpc("G"), "7")
    db7 = build(parse_tpc("Db"), "7")
    g7_tones = set(chord_tpcs(g7))
    db7_tones = set(chord_tpcs(db7))
    assert parse_tpc("F") in g7_tones and parse_tpc("F") in db7_tones
    assert parse_tpc("B") in g7_tones and parse_tpc("Cb") in db7_tones
    assert parse_tpc("B") - parse_tpc("Cb") == 12


def test_slash_chord_symbol() -> None:
    c = build(parse_tpc("C"), "maj7", bass=parse_tpc("E"))
    assert symbol(c) == "Cmaj7/E"


def test_dim7_spelling() -> None:
    d = build(parse_tpc("C"), "dim7")
    assert [tpc_name(t) for t in chord_tpcs(d)] == ["C", "Eb", "Gb", "Bbb"]


def test_major_sixth_chord_spelling() -> None:
    c = build(-1, "6")
    assert chord_tpcs(c) == (-1, 3, 0, 2)
    assert symbol(c) == "F6"


def test_minor_sixth_chord_spelling() -> None:
    c = build(2, "m6")
    assert chord_tpcs(c) == (2, -1, 3, 5)
    assert symbol(c) == "Dm6"
