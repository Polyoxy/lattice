from hypothesis import given, settings
from hypothesis import strategies as st

from lattice import make_beat
from lattice.cards import CONDUCTOR, FAIYAZ, MOLINA, TUNISIA
from lattice.harmony.elaborate import Segment
from lattice.model import Event, Role
from lattice.theory.pitch import SpelledPitch, pitch_class
from lattice.voicing.constraints import violates_lil, violates_min9

_CARDS = {"faiyaz": FAIYAZ, "conductor": CONDUCTOR, "molina": MOLINA, "tunisia": TUNISIA}


@settings(max_examples=15, deadline=None)
@given(
    seed=st.integers(0, 2**31 - 1),
    card_name=st.sampled_from(sorted(_CARDS)),
    key=st.sampled_from(["Am", "C#m", "Gm", "D", "Dm"]),
)
def test_beat_invariants(seed: int, card_name: str, key: str) -> None:
    card = _CARDS[card_name]
    beat = make_beat(style=card, key=key, bpm=80, bars=4, n=1, seed=seed)[0]

    # Exact bound for the A-section: beat.pocket is the realized swing/snap/clap
    # actually baked into parts_a/parts_b's micro_ms (api.py reuses one rng spawn
    # key for both, so their pocket draws are identical by construction).
    micro_bound = (
        (beat.pocket.swing - 0.5) * (60000 / beat.bpm)
        + max(abs(beat.pocket.snap_ms), abs(beat.pocket.clap_ms))
        + 6 * card.timing_sigma_ms
    )
    # The bridge is rendered from its own independent rng spawn key, so its
    # realized pocket differs from beat.pocket and isn't captured anywhere on
    # SectionRender. Bound it from the card's configured ranges instead of a
    # mismatched section's realized sample.
    bridge_micro_bound = (
        max(abs(card.swing_band[0] - 0.5), abs(card.swing_band[1] - 0.5)) * (60000 / beat.bpm)
        + max(
            abs(card.snap_rush_ms[0]), abs(card.snap_rush_ms[1]),
            abs(card.clap_drag_ms[0]), abs(card.clap_drag_ms[1]),
        )
        + 6 * card.timing_sigma_ms
    )

    def check_section(
        segments: tuple[Segment, ...],
        voicings: tuple[tuple[SpelledPitch, ...], ...],
        parts_iterable: tuple[dict[Role, tuple[Event, ...]], ...],
        bound: float,
    ) -> None:
        for seg, stack in zip(segments, voicings, strict=True):
            assert not violates_min9(stack, seg.chord)
            assert not violates_lil(stack)
            midis = [p.midi for p in stack]
            assert min(midis) >= card.register_lo and max(midis) <= card.register_hi
            assert max(midis) - min(midis) <= 24

        counts: dict[int, int] = {}
        for s in segments:
            counts[s.start_slot // 8] = counts.get(s.start_slot // 8, 0) + 1
        assert max(counts.values()) <= card.max_changes_per_bar

        for parts in parts_iterable:
            for events in parts.values():
                for e in events:
                    assert e.tick >= 0
                    assert abs(e.micro_ms) <= bound + 1e-6
                    assert 1 <= e.vel <= 127

    def check_sub_lock(segments: tuple[Segment, ...], sub_events: tuple[Event, ...]) -> None:
        sub_pitch_by_range = {
            (s.start_slot * 480): pitch_class(s.chord.root) for s in segments
        }
        for e in sub_events:
            assert e.pitch is not None and e.pitch % 12 == sub_pitch_by_range[e.tick]

    check_section(beat.segments, beat.voicings, (beat.parts_a, beat.parts_b), micro_bound)
    check_sub_lock(beat.segments, beat.parts_a[Role.SUB])

    if beat.section_b is not None:
        check_section(
            beat.section_b.segments,
            beat.section_b.voicings,
            (beat.section_b.parts_a, beat.section_b.parts_b),
            bridge_micro_bound,
        )
        check_sub_lock(beat.section_b.segments, beat.section_b.parts_a[Role.SUB])

    other = make_beat(style=card, key=key, bpm=80, bars=4, n=1, seed=seed)[0]
    assert beat.to_json() == other.to_json()
