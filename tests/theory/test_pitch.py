import pytest

from lattice.theory.pitch import (
    SpelledPitch,
    alteration,
    letter,
    parse_pitch,
    parse_tpc,
    pitch_class,
    same_pitch_class,
    tpc_name,
)


def test_line_of_fifths_anchor_points() -> None:
    assert parse_tpc("C") == 0
    assert parse_tpc("G") == 1
    assert parse_tpc("F") == -1
    assert parse_tpc("C#") == 7
    assert parse_tpc("Db") == -5
    assert parse_tpc("B#") == 12
    assert parse_tpc("Cb") == -7
    assert parse_tpc("Fx") == 13


def test_pitch_class_projection() -> None:
    assert pitch_class(parse_tpc("C#")) == 1
    assert pitch_class(parse_tpc("Db")) == 1
    assert pitch_class(parse_tpc("B#")) == 0
    assert pitch_class(parse_tpc("Cb")) == 11


def test_letter_and_alteration() -> None:
    assert (letter(7), alteration(7)) == ("C", 1)
    assert (letter(-5), alteration(-5)) == ("D", -1)
    assert (letter(-2), alteration(-2)) == ("B", -1)
    assert alteration(0) == 0
    assert alteration(-8) == -1


def test_names_round_trip() -> None:
    for name in ["C", "F#", "Bb", "Ebb", "Ax", "Cb", "B#"]:
        assert tpc_name(parse_tpc(name)) == name


def test_spelling_survives_where_midi_collapses() -> None:
    c_sharp = SpelledPitch(parse_tpc("C#"), 4)
    d_flat = SpelledPitch(parse_tpc("Db"), 4)
    assert c_sharp.midi == d_flat.midi == 61
    assert c_sharp != d_flat
    assert same_pitch_class(c_sharp.tpc, d_flat.tpc)
    assert not same_pitch_class(parse_tpc("C"), parse_tpc("D"))


def test_octave_boundary_projection() -> None:
    assert SpelledPitch(parse_tpc("Cb"), 4).midi == 59
    assert SpelledPitch(parse_tpc("B#"), 3).midi == 60
    assert SpelledPitch(parse_tpc("A"), 4).midi == 69


def test_parse_pitch() -> None:
    p = parse_pitch("Bb3")
    assert (p.tpc, p.octave, p.midi) == (-2, 3, 58)
    assert p.name() == "Bb3"
    with pytest.raises(ValueError):
        parse_pitch("H4")
