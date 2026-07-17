import numpy as np

from lattice.cards import get_card
from lattice.groove.strings import pad_events
from lattice.harmony.elaborate import elaborate
from lattice.harmony.grammar import candidate_loops
from lattice.theory.key import parse_key
from lattice.voicing.realize import realize


def test_pad_sustains_cover_segments_in_register() -> None:
    card = get_card("ballroom")
    rng = np.random.default_rng(11)
    key = parse_key("F")
    loop = candidate_loops(card, key, 4)[0]
    segments = elaborate(loop, card, rng)
    voicings = realize(segments, card)
    events = pad_events(segments, voicings, 4)
    assert events
    starts = {s.start_slot * 480 for s in segments}
    assert {e.tick for e in events} <= starts
    assert all(55 <= e.pitch <= 88 for e in events if e.pitch is not None)
    assert all(e.dur > 0 for e in events)
