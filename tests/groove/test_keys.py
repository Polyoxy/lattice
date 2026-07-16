import numpy as np

from lattice.cards import CONDUCTOR, FAIYAZ
from lattice.groove.keys import keys_events
from lattice.harmony.elaborate import Segment
from lattice.theory.chord import build
from lattice.theory.pitch import SpelledPitch, parse_tpc


def _fixture() -> tuple[tuple[Segment, ...], tuple[tuple[SpelledPitch, ...], ...]]:
    segs = (
        Segment(build(parse_tpc("A"), "m7"), "i7", 0, 16),
        Segment(build(parse_tpc("E"), "m7"), "v7", 16, 16),
    )
    voicings = (
        (SpelledPitch(0, 4), SpelledPitch(4, 4)),
        (SpelledPitch(1, 4), SpelledPitch(5, 4)),
    )
    return segs, voicings


def test_sustain_mode_one_attack_per_segment() -> None:
    segs, voicings = _fixture()
    card = FAIYAZ.override(p_keys_anticipation=0.0)
    events = keys_events(segs, voicings, bars=4, card=card, rng=np.random.default_rng(0))
    attacks = sorted({e.tick for e in events})
    assert attacks == [0, 16 * 480]


def test_anticipation_pushes_by_an_eighth_when_forced() -> None:
    segs, voicings = _fixture()
    card = FAIYAZ.override(p_keys_anticipation=1.0)
    events = keys_events(segs, voicings, bars=4, card=card, rng=np.random.default_rng(0))
    attacks = sorted({e.tick for e in events})
    assert attacks == [0, 16 * 480 - 480]


def test_chop_mode_reattacks_within_segment() -> None:
    segs, voicings = _fixture()
    events = keys_events(segs, voicings, bars=4, card=CONDUCTOR, rng=np.random.default_rng(0))
    first_seg_attacks = {e.tick for e in events if e.tick < 16 * 480}
    assert len(first_seg_attacks) >= 2


def test_chop_mode_clips_offsets_on_short_segments() -> None:
    from lattice.harmony.elaborate import Segment
    from lattice.theory.chord import build
    from lattice.theory.pitch import parse_tpc

    short = (
        Segment(build(parse_tpc("A"), "m7"), "i7", 0, 2),
        Segment(build(parse_tpc("E"), "m7"), "v7", 2, 30),
    )
    voicings = (
        (SpelledPitch(0, 4), SpelledPitch(4, 4)),
        (SpelledPitch(1, 4), SpelledPitch(5, 4)),
    )
    events = keys_events(short, voicings, bars=4, card=CONDUCTOR, rng=np.random.default_rng(0))
    first_seg_attacks = {e.tick for e in events if e.tick < 2 * 480}
    assert first_seg_attacks == {0}
