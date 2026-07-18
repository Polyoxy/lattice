from lattice.cards import FAIYAZ
from lattice.harmony.grammar import Loop
from lattice.harmony.functions import build_function
from lattice.harmony.score import canonical_rotation, loop_score, rank, tension, vl_distance
from lattice.theory.chord import build
from lattice.theory.key import parse_key
from lattice.theory.pitch import parse_tpc


def _loop(key_s: str, names: tuple[str, ...]) -> Loop:
    k = parse_key(key_s)
    return Loop(k, tuple(build_function(k, n) for n in names), bars=4)


def test_tension_orders_alteration_density() -> None:
    k = parse_key("Cm")
    plain = build(parse_tpc("G"), "m7")
    spicy = build(parse_tpc("G"), "7b13")
    assert tension(spicy, k) > tension(plain, k)


def test_vl_distance_trust_loop_is_tiny() -> None:
    dbmaj7 = build(parse_tpc("Db"), "maj7")
    fm7 = build(parse_tpc("F"), "m7")
    assert vl_distance(dbmaj7, fm7) <= 2


def test_documented_loop_outranks_junk() -> None:
    trust = _loop("Fm", ("bVImaj7", "i7"))
    junk = _loop("Fm", ("bII", "IV7"))
    assert loop_score(trust, FAIYAZ) > loop_score(junk, FAIYAZ)


def test_canonical_rotation() -> None:
    assert canonical_rotation(("v7", "i7")) == ("i7", "v7")
    assert canonical_rotation(("i7", "v7")) == ("i7", "v7")


def test_rank_dedupes_root_motion_and_returns_n() -> None:
    loops = [
        _loop("Am", ("i7", "v7")),
        _loop("Am", ("i9", "v7")),
        _loop("Am", ("i7", "iv7")),
        _loop("Am", ("bVImaj7", "i7")),
    ]
    top = rank(loops, FAIYAZ, n=3)
    assert len(top) == 3
    assert len({tuple(fc.name for fc in lp.items) for lp in top}) == 3


def test_idiom_shapes_are_reachable_and_fire() -> None:
    from lattice.harmony.score import IDIOM_SHAPES

    assert len(IDIOM_SHAPES) == 24
    assert all(canonical_rotation(s) == s for s in IDIOM_SHAPES)
    rs = _loop("Bm", ("iv6add9", "v7", "i7", "bVImaj7"))
    non_idiom = _loop("Bm", ("iv6add9", "v7", "i7", "bIII"))
    assert loop_score(rs, FAIYAZ) > loop_score(non_idiom, FAIYAZ)


def test_contrast_rewards_difference_and_cadence() -> None:
    from lattice.harmony.score import contrast
    from lattice.harmony.functions import build_function
    from lattice.harmony.grammar import Loop
    from lattice.theory.key import parse_key

    key = parse_key("Dm")
    vamp = Loop(key, tuple(build_function(key, n) for n in ("i7", "bII")), bars=4)
    same = Loop(key, tuple(build_function(key, n) for n in ("i7", "bII")), bars=4)
    bridge = Loop(key, tuple(build_function(key, n) for n in ("iv7", "bVII7", "i7", "V7")), bars=4)
    assert contrast(vamp, bridge) > contrast(vamp, same)
    assert contrast(vamp, same) < 1.0


def test_card_scoped_shapes_fire_only_for_their_card() -> None:
    from lattice.cards import get_card
    from lattice.harmony.score import CARD_IDIOM_SHAPES, IDIOM_SHAPES

    lament = ("i7", "bVII7", "bVImaj7", "V7")
    loop = _loop("Dm", lament)
    conductor = get_card("conductor")
    base = loop_score(loop, conductor)
    assert canonical_rotation(lament) in CARD_IDIOM_SHAPES["chase"]
    assert canonical_rotation(lament) not in IDIOM_SHAPES
    assert loop_score(loop, conductor) == base
