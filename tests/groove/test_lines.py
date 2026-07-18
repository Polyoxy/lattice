import numpy as np

from lattice.cards import get_card
from lattice.groove.lines import answer_motif, conversation, state_motif
from lattice.harmony.elaborate import Segment, elaborate
from lattice.harmony.grammar import candidate_loops
from lattice.model import Role
from lattice.theory.chord import build
from lattice.theory.key import parse_key


def _seg(quality: str = "m7") -> Segment:
    return Segment(build(2, quality), "i7", 0, 16)


def test_motif_contours_lock() -> None:
    card = get_card("chase")
    directions = []
    for motif in card.motifs:
        events = state_motif(motif, _seg(), (60, 76), 0)
        pitches = [e.pitch for e in events if e.pitch is not None]
        directions.append(tuple(np.sign(np.diff(pitches)).astype(int)))
    assert directions == [(-1,), (1, -1), (-1, -1, -1), (0, 0), (1, 1)]


def test_answers_derive_from_calls() -> None:
    card = get_card("chase")
    call = state_motif(card.motifs[1], _seg(), (60, 76), 0)
    late = answer_motif(call, "displace", _seg())
    assert [e.tick - c.tick for e, c in zip(late, call, strict=True)] == [480] * len(call)
    cut = answer_motif(call, "truncate", _seg())
    assert len(cut) == len(call) - 1
    denied = answer_motif(call, "deny", _seg())
    assert denied[-1].pitch != call[-1].pitch


def test_conversation_windows_never_collide() -> None:
    card = get_card("chase")
    rng = np.random.default_rng(9)
    key = parse_key("Dm")
    loop = candidate_loops(card, key, 4)[0]
    segments = elaborate(loop, card, rng)
    parts = conversation(
        segments, card, 4, np.random.default_rng(3),
        caller=Role.KEYS, answerers=(Role.PAD,), density_bars=2,
    )
    call_spans = [(e.tick, e.tick + e.dur) for e in parts[Role.KEYS]]
    ans_spans = [(e.tick, e.tick + e.dur) for e in parts[Role.PAD]]
    for cs in call_spans:
        for asp in ans_spans:
            assert cs[1] <= asp[0] or asp[1] <= cs[0]


def test_conversation_bridge_density_one_never_collides() -> None:
    # Task-5 reviewer's follow-up (task-5-report.md concern #1): density_bars=1 is only
    # ever actually wired for the bridge (caller=LEAD, answerers=(PAD, KEYS)), and that
    # shape's collision safety was previously proven only by an uncommitted sweep script.
    # Mirrors test_conversation_windows_never_collide's structure over a real bridge loop,
    # built the same way api.py builds one (function/major_function/loop_len overridden).
    card = get_card("chase")
    bridge_card = card.override(
        function_pool=card.bridge_function_pool,
        major_function_pool=card.bridge_major_function_pool,
        loop_len_weights=card.bridge_len_weights,
    )
    rng = np.random.default_rng(11)
    key = parse_key("Dm")
    loop = candidate_loops(bridge_card, key, 4)[0]
    segments = elaborate(loop, bridge_card, rng)
    parts = conversation(
        segments, card, 4, np.random.default_rng(13),
        caller=Role.LEAD, answerers=(Role.PAD, Role.KEYS), density_bars=1,
    )
    call_spans = [(e.tick, e.tick + e.dur) for e in parts[Role.LEAD]]
    for r in (Role.PAD, Role.KEYS):
        ans_spans = [(e.tick, e.tick + e.dur) for e in parts[r]]
        for cs in call_spans:
            for asp in ans_spans:
                assert cs[1] <= asp[0] or asp[1] <= cs[0]


def test_avoid_filter_resolves_sustained_clash_to_chord_tone() -> None:
    # Offset -4 from a Dm7 root spells Bb, a half-step above the chord's 5th (A) —
    # a textbook avoid-note clash (violates_min9). A single-note/single-slot motif
    # forces dur=960 (the "last note" rule), so the filter must fire; proves the
    # mechanism isn't inert (the five card motifs never happen to trigger it — see
    # report) and resolves to the nearest real chord tone rather than dropping it.
    motif = ((-4,), (0,))
    events = state_motif(motif, _seg(), (60, 76), 0)
    assert len(events) == 1
    assert events[0].pitch == 69  # A4: nearest chord tone to the filtered Bb candidate


def test_bend_mock_pitches_lock() -> None:
    # Reviewer-executed values against the live engine (Dm7, register (60, 76), window 0),
    # locking both transforms' branch behavior: bend's chord-tone (2-semitone) branch fires
    # for sigh/push/defiance, the 1-semitone fallback for cry/spiral.
    card = get_card("chase")
    bend_finals = []
    mock_lines = []
    for motif in card.motifs:
        call = state_motif(motif, _seg(), (60, 76), 0)
        bend_finals.append(answer_motif(call, "bend", _seg())[-1].pitch)
        mock_lines.append(tuple(e.pitch for e in answer_motif(call, "mock", _seg())))
    assert bend_finals == [60, 68, 56, 60, 72]
    assert mock_lines == [
        (67, 64), (71, 72, 71), (64, 62, 60, 59), (64, 64, 64), (71, 74, 76),
    ]


def test_conversation_answers_only_excludes_caller_key() -> None:
    card = get_card("chase")
    rng = np.random.default_rng(1)
    key = parse_key("Dm")
    loop = candidate_loops(card, key, 4)[0]
    segments = elaborate(loop, card, rng)
    parts = conversation(
        segments, card, 4, np.random.default_rng(2),
        caller=Role.LEAD, answerers=(Role.PAD, Role.KEYS), density_bars=1,
        answers_only=True,
    )
    assert Role.LEAD not in parts
    assert set(parts) == {Role.PAD, Role.KEYS}
    assert any(parts.values())
