from lattice.cards import FAIYAZ
from lattice.harmony.grammar import Loop, candidate_loops, enumerate_progressions, expressible
from lattice.harmony.functions import build_function
from lattice.theory.key import parse_key


def test_enumerate_no_adjacent_repeats_and_no_cyclic_seam_repeat() -> None:
    progs = enumerate_progressions(("i7", "v7", "iv7"), 3)
    assert ("i7", "i7", "v7") not in progs
    assert ("i7", "v7", "i7") not in progs
    assert ("i7", "v7", "iv7") in progs


def test_enumeration_is_capped_and_deterministic() -> None:
    pool = tuple(f"f{i}" for i in range(14))
    a = enumerate_progressions(pool, 4)
    b = enumerate_progressions(pool, 4)
    assert a == b and len(a) <= 20000


def test_documented_shapes_are_expressible() -> None:
    assert expressible(FAIYAZ, parse_key("Fm"), ("bVImaj7", "i7"))
    assert expressible(FAIYAZ, parse_key("Am"), ("i7", "v7"))
    assert expressible(FAIYAZ, parse_key("Bm"), ("iv6add9", "v7", "i7", "bVImaj7"))
    assert expressible(FAIYAZ, parse_key("C#m"), ("i7", "bII"))
    assert expressible(FAIYAZ, parse_key("E"), ("ii9", "V7maj", "Imaj7", "vi7"))
    assert not expressible(FAIYAZ, parse_key("Am"), ("i7", "nonsense"))


def test_candidates_include_kicker_final_loops() -> None:
    loops = candidate_loops(FAIYAZ, parse_key("Dm"), bars=4)
    names = {loop.names() for loop in loops}
    assert ("i7", "v7") in names
    assert ("i7", "V7b13") in names


def test_all_candidates_satisfy_loop_invariants() -> None:
    for loop in candidate_loops(FAIYAZ, parse_key("Dm"), bars=4):
        names = loop.names()
        for a, b in zip(names, names[1:], strict=False):
            assert a != b
        if len(names) > 1:
            assert names[0] != names[-1]


def test_no_tritone_or_mediant_functions_in_faiyaz_candidates() -> None:
    loops = candidate_loops(FAIYAZ, parse_key("Am"), bars=4)
    for loop in loops:
        for item in loop.items:
            assert "tritone" not in item.roman and "mediant" not in item.roman


def test_loop_slots_cover_bars_evenly() -> None:
    k = parse_key("Am")
    loop = Loop(k, (build_function(k, "i7"), build_function(k, "v7")), bars=4)
    slots = loop.slots()
    assert slots[0][1] == 0 and slots[0][2] == 16
    assert slots[1][1] == 16 and slots[1][2] == 16
    loop3 = Loop(
        k,
        (build_function(k, "i7"), build_function(k, "iv7"), build_function(k, "v7")),
        bars=4,
    )
    assert sum(s[2] for s in loop3.slots()) == 32
