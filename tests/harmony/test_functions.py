from lattice.harmony.functions import build_function, pool_for
from lattice.harmony.score import _TONIC_NAMES
from lattice.theory.chord import chord_tpcs, symbol
from lattice.theory.key import parse_key
from lattice.theory.pitch import tpc_name


def test_documented_loops_spell_correctly() -> None:
    fm = parse_key("Fm")
    assert symbol(build_function(fm, "bVImaj7").chord) == "Dbmaj7"
    am = parse_key("Am")
    assert symbol(build_function(am, "v7").chord) == "Em7"
    bm = parse_key("Bm")
    assert symbol(build_function(bm, "iv6add9").chord) == "Em6add9"
    assert symbol(build_function(bm, "bVImaj7").chord) == "Gmaj7"
    cm = parse_key("Cm")
    assert symbol(build_function(cm, "V7b13").chord) == "G7b13"


def test_clouded_shimmer_is_nondiatonic_vii_m7() -> None:
    d = parse_key("D")
    fc = build_function(d, "vii_m7")
    assert symbol(fc.chord) == "C#m7"
    assert fc.roman == "vii(m7)"


def test_gravity_major_pool() -> None:
    e = parse_key("E")
    assert symbol(build_function(e, "ii9").chord) == "F#m9"
    assert symbol(build_function(e, "V7maj").chord) == "B7"


def test_pool_filters_by_mode() -> None:
    pool = ("i7", "v7", "Imaj7", "ii9")
    assert pool_for(parse_key("Am"), pool) == ("i7", "v7")
    assert pool_for(parse_key("C"), pool) == ("Imaj7", "ii9")


def test_ballroom_functions_resolve_in_f_major() -> None:
    key = parse_key("F")
    for name, root, quality in [
        ("I6", -1, "6"),
        ("I6add9", -1, "6add9"),
        ("IV6", -2, "6"),
        ("iv6", -2, "m6"),
        ("V9", 0, "9"),
        ("II7", 1, "7"),
        ("III7", 3, "7"),
        ("VI7", 2, "7"),
        ("#idim7", 6, "dim7"),
    ]:
        fc = build_function(key, name)
        assert fc.chord.root == root, name
        assert symbol(fc.chord).startswith(tpc_name(root)), name


def test_sharp_one_diminished_spells_sharp() -> None:
    fc = build_function(parse_key("C"), "#idim7")
    assert chord_tpcs(fc.chord) == (7, 4, 1, -2)


def test_added_sixth_tonic_scores_as_tonic() -> None:
    assert "I6" in _TONIC_NAMES and "I6add9" in _TONIC_NAMES
