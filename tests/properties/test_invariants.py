from hypothesis import given, settings
from hypothesis import strategies as st

from lattice import make_beat
from lattice.cards import CONDUCTOR, FAIYAZ, MOLINA
from lattice.model import Role
from lattice.theory.pitch import pitch_class
from lattice.voicing.constraints import violates_lil, violates_min9

_CARDS = {"faiyaz": FAIYAZ, "conductor": CONDUCTOR, "molina": MOLINA}


@settings(max_examples=15, deadline=None)
@given(
    seed=st.integers(0, 2**31 - 1),
    card_name=st.sampled_from(sorted(_CARDS)),
    key=st.sampled_from(["Am", "C#m", "Gm", "D"]),
)
def test_beat_invariants(seed: int, card_name: str, key: str) -> None:
    card = _CARDS[card_name]
    beat = make_beat(style=card, key=key, bpm=80, bars=4, n=1, seed=seed)[0]

    for seg, stack in zip(beat.segments, beat.voicings, strict=True):
        assert not violates_min9(stack, seg.chord)
        assert not violates_lil(stack)
        midis = [p.midi for p in stack]
        assert min(midis) >= card.register_lo and max(midis) <= card.register_hi
        assert max(midis) - min(midis) <= 24

    counts: dict[int, int] = {}
    for s in beat.segments:
        counts[s.start_slot // 8] = counts.get(s.start_slot // 8, 0) + 1
    assert max(counts.values()) <= card.max_changes_per_bar

    sub_pitch_by_range = {
        (s.start_slot * 480): pitch_class(s.chord.root) for s in beat.segments
    }
    for e in beat.parts_a[Role.SUB]:
        assert e.pitch is not None and e.pitch % 12 == sub_pitch_by_range[e.tick]

    micro_bound = (
        (beat.pocket.swing - 0.5) * (60000 / beat.bpm)
        + max(abs(beat.pocket.snap_ms), abs(beat.pocket.clap_ms))
        + 6 * card.timing_sigma_ms
    )
    for parts in (beat.parts_a, beat.parts_b):
        for events in parts.values():
            for e in events:
                assert e.tick >= 0
                assert abs(e.micro_ms) <= micro_bound + 1e-6
                assert 1 <= e.vel <= 127

    other = make_beat(style=card, key=key, bpm=80, bars=4, n=1, seed=seed)[0]
    assert beat.to_json() == other.to_json()
