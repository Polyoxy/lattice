import numpy as np

from lattice import make_beat
from lattice.beat import Beat
from lattice.cards import CONDUCTOR, FAIYAZ, get_card
from lattice.groove.keys import keys_events
from lattice.groove.pocket import apply_pocket
from lattice.harmony.elaborate import Segment
from lattice.model import Event, Role
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


def _stride_events(seed: int = 3) -> Beat:
    beats = make_beat(style="ballroom", key="F", bpm=112, bars=2, n=1, seed=seed)
    return beats[0]


def test_stride_left_hand_alternates_low_register() -> None:
    beat = _stride_events()
    lh = [e for e in beat.parts_a[Role.KEYS] if e.tick % 1920 == 0 and e.pitch is not None]
    assert lh, "no left-hand events"
    assert all(40 <= e.pitch <= 55 for e in lh if e.pitch is not None)


def test_stride_chords_sit_on_two_and_four() -> None:
    beat = _stride_events()
    chords = [e for e in beat.parts_a[Role.KEYS] if e.tick % 1920 in (960, 480)]
    assert chords
    assert all(48 <= e.pitch <= 76 for e in chords if e.pitch is not None)


def test_stride_left_hand_uses_chord_fifth_for_diminished() -> None:
    card = get_card("ballroom")
    seg = Segment(build(7, "dim7"), "#i dim7", 0, 16)
    stack = (SpelledPitch(7, 5), SpelledPitch(4, 5), SpelledPitch(1, 5))
    events = keys_events((seg,), (stack,), 2, card, np.random.default_rng(0))
    lh_pcs = {e.pitch % 12 for e in events if e.tick % 1920 == 0 and e.pitch is not None}
    assert 7 in lh_pcs
    assert 8 not in lh_pcs


def test_stride_anticipation_lands_on_swung_offbeat() -> None:
    # RH anticipation pushes onset to t - 480, i.e. tick % 960 == 480 — the exact
    # remainder apply_pocket's swing rule matches. Bound is sigma-independent:
    # the swing_band floor (0.58) minus the harshest possible negative jitter
    # (clipped at 6 sigma) still nets a large positive gain, for any rng draw.
    card = get_card("ballroom")
    bpm = 112
    beat_ms = 60000.0 / bpm
    min_gain = (card.swing_band[0] - 0.5) * beat_ms - 6 * card.timing_sigma_ms
    parts = {Role.KEYS: (Event(480, 720, 66, pitch=60),)}
    for seed in range(10):
        out, _ = apply_pocket(parts, card, bpm, np.random.default_rng(seed))
        assert out[Role.KEYS][0].micro_ms >= min_gain


def test_stride_anticipation_stays_swung_regression_guard() -> None:
    # Pinned seed: scanning ballroom seeds 1-30, seed 3 is the first whose parts_a
    # carries an RH anticipation (tick % 960 == 480). Guards against the
    # swing-band-inert regression going dead again silently.
    beat = make_beat(style="ballroom", key="F", bpm=112, bars=2, n=1, seed=3)[0]
    anticipated = [e for e in beat.parts_a[Role.KEYS] if e.tick % 960 == 480]
    assert anticipated
    mean_micro = sum(e.micro_ms for e in anticipated) / len(anticipated)
    assert mean_micro > 0


def test_duel_motor_covers_every_eighth() -> None:
    beat = make_beat(style="chase", key="Dm", bpm=160, bars=2, n=1, seed=5)[0]
    lh = [e for e in beat.parts_a[Role.KEYS] if e.pitch is not None and 40 <= e.pitch <= 52]
    ticks = {e.tick for e in lh}
    assert {i * 480 for i in range(16)} <= ticks


def test_duel_rh_stays_above_motor() -> None:
    beat = make_beat(style="chase", key="Dm", bpm=160, bars=2, n=1, seed=5)[0]
    rh = [e for e in beat.parts_a[Role.KEYS] if e.pitch is not None and e.pitch > 52]
    assert rh
    assert all(56 <= e.pitch <= 88 for e in rh)


def test_duel_lh_cycles_root_fifth_seventh_and_bumps_beat_one() -> None:
    # Dm7 carries a real m7 (pc 0 = C), so the third step of the cycle should land
    # there rather than falling back to the fifth — proves the "seventh when present"
    # branch actually fires, not just its "else fifth" sibling.
    seg = Segment(build(parse_tpc("D"), "m7"), "i7", 0, 8)
    stack = (SpelledPitch(0, 4), SpelledPitch(4, 4))
    card = get_card("chase").override(keys_pattern="duel_low")
    events = keys_events((seg,), (stack,), 1, card, np.random.default_rng(0))
    lh = sorted(events, key=lambda e: e.tick)
    assert len(lh) == 8
    pcs = [(e.pitch or 0) % 12 for e in lh[:4]]
    assert pcs == [2, 9, 0, 9]  # D, A, C, A -> root, fifth, m7, fifth
    assert lh[0].vel == 92 + 6  # beat 1 of bar 0 bumped
    assert lh[1].vel == 74


def test_duel_lh_falls_back_to_fifth_without_a_seventh() -> None:
    seg = Segment(build(parse_tpc("D"), ""), "I", 0, 8)  # plain major triad, no 7th
    stack = (SpelledPitch(0, 4), SpelledPitch(4, 4))
    card = get_card("chase").override(keys_pattern="duel_low")
    events = keys_events((seg,), (stack,), 1, card, np.random.default_rng(0))
    lh = sorted(events, key=lambda e: e.tick)
    assert [(e.pitch or 0) % 12 for e in lh[:4]] == [2, 9, 9, 9]  # root, fifth, fifth, fifth


def test_duel_stab_skipped_only_on_the_overlapped_slot() -> None:
    seg = Segment(build(parse_tpc("D"), "m7"), "i7", 0, 16)
    stack = (SpelledPitch(0, 4), SpelledPitch(4, 4), SpelledPitch(6, 4))
    card = get_card("chase").override(keys_pattern="duel")
    call = (Event(1440, 480, 90, pitch=67),)  # sits exactly on bar 0's slot-3 stab tick
    events = keys_events((seg,), (stack,), 2, card, np.random.default_rng(0), call)
    stabs = {e.tick for e in events if e.vel == 68}
    assert 1440 not in stabs
    assert 2880 in stabs  # the other stab slot in the same bar is unaffected


def test_duel_stab_skipped_by_avoid_span() -> None:
    # Same overlap as the duel_events case above, but arriving via avoid_spans
    # instead — a PAD/LEAD answer rather than the KEYS-role call itself.
    seg = Segment(build(parse_tpc("D"), "m7"), "i7", 0, 16)
    stack = (SpelledPitch(0, 4), SpelledPitch(4, 4), SpelledPitch(6, 4))
    card = get_card("chase").override(keys_pattern="duel")
    avoid_spans = ((1440, 1920),)  # an answer sitting on bar 0's slot-3 stab tick
    events = keys_events((seg,), (stack,), 2, card, np.random.default_rng(0), (), avoid_spans)
    stabs = {e.tick for e in events if e.vel == 68}
    assert 1440 not in stabs
    assert 2880 in stabs  # the other stab slot in the same bar is unaffected


def test_duel_stabs_never_overlap_pad_or_lead_answers_across_seeds() -> None:
    # Mirrors the review's own measurement (78 overlapping stab/answer pairs
    # across 20 seeds pre-fix): regenerate real chase beats and check the RH
    # register (pitch > 52 — LH motor tops out at 52, same convention as
    # test_duel_rh_stays_above_motor) never lands inside a PAD/LEAD answer's
    # time span. Calls share that register too but are excluded by
    # construction (the conversation windows never overlap calls and
    # answers), so any hit here can only be an unskipped stab.
    for seed in range(1, 21):
        beat = make_beat(style="chase", bars=4, n=1, seed=seed)[0]
        answer_spans = [
            (e.tick, e.tick + e.dur)
            for e in (*beat.parts_a[Role.PAD], *beat.parts_a[Role.LEAD])
        ]
        rh = [e for e in beat.parts_a[Role.KEYS] if e.pitch is not None and e.pitch > 52]
        for e in rh:
            for start, end in answer_spans:
                overlaps = start < e.tick + e.dur and e.tick < end
                msg = f"seed {seed}: keys event at {e.tick} overlaps answer ({start}, {end})"
                assert not overlaps, msg
