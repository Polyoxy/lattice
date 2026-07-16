from lattice.cards import FAIYAZ, MOLINA
from lattice.harmony.elaborate import Segment
from lattice.theory.chord import build
from lattice.theory.pitch import parse_tpc, pitch_class
from lattice.voicing.constraints import violates_lil, violates_min9
from lattice.voicing.realize import realize
from lattice.voicing.templates import stack_candidates
from lattice.theory.pitch import SpelledPitch


def _sp(name: str, octave: int) -> SpelledPitch:
    return SpelledPitch(parse_tpc(name), octave)


def test_min9_rejected_on_maj7_but_allowed_over_dominant_root() -> None:
    cmaj7 = build(parse_tpc("C"), "maj7")
    bad = (_sp("B", 3), _sp("E", 4), _sp("G", 4), _sp("C", 5))
    assert violates_min9(bad, cmaj7)
    g7b9 = build(parse_tpc("G"), "7b9")
    ok = (_sp("G", 3), _sp("B", 3), _sp("F", 4), _sp("Ab", 4))
    assert not violates_min9(ok, g7b9)


def test_lil_rejects_low_major_third() -> None:
    assert violates_lil((_sp("G", 2), _sp("B", 2)))
    assert not violates_lil((_sp("G", 3), _sp("B", 3)))


def test_faiyaz_stacks_are_rootless_mid_register() -> None:
    am9 = build(parse_tpc("A"), "m9")
    stacks = stack_candidates(am9, FAIYAZ, bass_covers_root=True)
    assert stacks
    root_pc = pitch_class(parse_tpc("A"))
    for stack in stacks:
        assert all(p.midi % 12 != root_pc for p in stack)
        assert all(FAIYAZ.register_lo <= p.midi <= FAIYAZ.register_hi for p in stack)


def test_molina_dominant_gets_us_triad_and_sus_candidates() -> None:
    g7b13 = build(parse_tpc("G"), "7b13")
    stacks = stack_candidates(g7b13, MOLINA, bass_covers_root=True)
    assert len(stacks) >= 4


def test_realize_minimizes_motion_on_trust_loop() -> None:
    dbmaj7 = build(parse_tpc("Db"), "maj7")
    fm7 = build(parse_tpc("F"), "m7")
    segs = (
        Segment(dbmaj7, "bVImaj7", 0, 16),
        Segment(fm7, "i7", 16, 16),
    )
    voicings = realize(segs, FAIYAZ)
    assert len(voicings) == 2
    tops = [max(p.midi for p in v) for v in voicings]
    assert abs(tops[0] - tops[1]) <= 4


def test_molina_m9_gets_so_what_quartal() -> None:
    am9 = build(parse_tpc("A"), "m9")
    stacks = stack_candidates(am9, MOLINA, bass_covers_root=True)
    gaps = [
        tuple(b.midi - a.midi for a, b in zip(s, s[1:], strict=False)) for s in stacks
    ]
    assert (5, 5, 5, 4) in gaps


def test_every_card_center_voices_every_pool_function() -> None:
    from lattice.cards import CONDUCTOR
    from lattice.harmony.functions import build_function
    from lattice.theory.key import parse_key

    for card in (FAIYAZ, CONDUCTOR, MOLINA):
        for centers, pool in (
            (card.centers, card.function_pool),
            (card.major_centers, card.major_function_pool),
        ):
            for center in centers:
                key = parse_key(center)
                for name in pool:
                    chord = build_function(key, name).chord
                    assert stack_candidates(chord, card, True), f"{card.name} {center} {name}"


def test_molina_m7_gets_add9_color() -> None:
    cm7 = build(parse_tpc("C"), "m7")
    stacks = stack_candidates(cm7, MOLINA, bass_covers_root=True)
    assert any(len(s) == 4 and any(p.midi % 12 == 2 for p in s) for s in stacks)


def test_seed_from_biases_opening_voicing_toward_seam() -> None:
    from lattice.harmony.elaborate import Segment
    from lattice.theory.chord import build
    from lattice.theory.pitch import SpelledPitch, parse_tpc
    from lattice.voicing.realize import realize

    segs = (Segment(build(parse_tpc("G"), "m7"), "iv7", 0, 16),)
    seed_high = (SpelledPitch(parse_tpc("D"), 5),)
    seed_low = (SpelledPitch(parse_tpc("D"), 3),)
    from lattice.cards import MOLINA

    top_high = max(realize(segs, MOLINA, seed_from=seed_high)[0], key=lambda p: p.midi).midi
    top_low = max(realize(segs, MOLINA, seed_from=seed_low)[0], key=lambda p: p.midi).midi
    assert top_high >= top_low


def test_seed_from_none_matches_default() -> None:
    from lattice.harmony.elaborate import Segment
    from lattice.theory.chord import build
    from lattice.theory.pitch import parse_tpc
    from lattice.voicing.realize import realize
    from lattice.cards import FAIYAZ

    segs = (
        Segment(build(parse_tpc("A"), "m9"), "i9", 0, 16),
        Segment(build(parse_tpc("F"), "maj7"), "bVImaj7", 16, 16),
    )
    assert realize(segs, FAIYAZ) == realize(segs, FAIYAZ, seed_from=None)
