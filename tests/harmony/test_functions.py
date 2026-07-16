from lattice.harmony.functions import build_function, pool_for
from lattice.theory.chord import symbol
from lattice.theory.key import parse_key


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
