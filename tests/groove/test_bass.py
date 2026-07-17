import numpy as np

from lattice.cards import FAIYAZ, StyleCard, get_card
from lattice.groove.bass import bass_parts
from lattice.harmony.elaborate import Segment, elaborate
from lattice.harmony.grammar import candidate_loops
from lattice.model import Role
from lattice.theory.chord import build
from lattice.theory.key import parse_key
from lattice.theory.pitch import parse_tpc, pitch_class


def _segs() -> tuple[Segment, ...]:
    return (
        Segment(build(parse_tpc("A"), "m9"), "i9", 0, 16),
        Segment(build(parse_tpc("F"), "maj7"), "bVImaj7", 16, 16),
    )


def _ballroom_segments() -> tuple[tuple[Segment, ...], StyleCard]:
    card = get_card("ballroom")
    rng = np.random.default_rng(7)
    key = parse_key("F")
    loop = candidate_loops(card, key, 4)[0]
    return elaborate(loop, card, rng), card


def test_two_feel_half_notes_in_register() -> None:
    segments, card = _ballroom_segments()
    parts = bass_parts(segments, card, np.random.default_rng(1))
    assert parts[Role.SUB] == ()
    events = parts[Role.BASS]
    assert events
    assert all(e.tick % 1920 == 0 for e in events)
    assert all(28 <= e.pitch <= 52 for e in events if e.pitch is not None)


def test_walk_quarters_and_approach() -> None:
    segments, card = _ballroom_segments()
    walk_card = card.override(bass_feel="walk")
    parts = bass_parts(segments, walk_card, np.random.default_rng(1))
    events = parts[Role.BASS]
    assert all(e.tick % 960 == 0 for e in events)
    assert all(28 <= e.pitch <= 52 for e in events if e.pitch is not None)
    ticks = sorted(e.tick for e in events)
    assert len(ticks) >= 4 * len(segments)


def test_sub_is_roots_only_and_tiles_segments() -> None:
    parts = bass_parts(_segs(), card=FAIYAZ, rng=np.random.default_rng(0))
    sub = parts[Role.SUB]
    assert len(sub) == 2
    assert sub[0].pitch is not None and sub[0].pitch % 12 == pitch_class(parse_tpc("A"))
    assert sub[1].pitch is not None and sub[1].pitch % 12 == pitch_class(parse_tpc("F"))
    assert all(26 <= e.pitch <= 38 for e in sub if e.pitch is not None)
    assert sub[0].tick == 0 and sub[0].dur == 16 * 480
    assert sub[1].tick == 16 * 480


def test_approach_note_resolves_by_semitone_when_forced() -> None:
    card = FAIYAZ.override(p_bass_approach=1.0, p_bass_stab=0.0)
    parts = bass_parts(_segs(), card=card, rng=np.random.default_rng(1))
    bass = parts[Role.BASS]
    boundary = 16 * 480
    approach = [e for e in bass if e.tick == boundary - 240]
    assert len(approach) == 1
    sub = parts[Role.SUB]
    next_pitch = sub[1].pitch
    assert next_pitch is not None and approach[0].pitch == next_pitch + 12 - 1


def test_csharp_sub_stays_in_range() -> None:
    from lattice.groove.bass import _sub_pitch
    from lattice.theory.pitch import parse_tpc

    assert _sub_pitch(parse_tpc("C#")) == 37
    for name in ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]:
        assert 26 <= _sub_pitch(parse_tpc(name)) <= 38


def test_stab_and_glide_forced() -> None:
    card = FAIYAZ.override(p_bass_stab=1.0, p_bass_approach=0.0, p_bass_glide=0.0)
    parts = bass_parts(_segs(), card=card, rng=np.random.default_rng(2))
    bass = parts[Role.BASS]
    stabs = [e for e in bass if e.tick in (1440, 1680)]
    assert [e.vel for e in stabs] == [72, 64]
    card2 = FAIYAZ.override(p_bass_approach=1.0, p_bass_glide=1.0, p_bass_stab=0.0)
    parts2 = bass_parts(_segs(), card=card2, rng=np.random.default_rng(3))
    assert any(e.glide for e in parts2[Role.BASS])


def test_approach_wins_stab_collision_on_four_slot_segments() -> None:
    from lattice.harmony.elaborate import Segment
    from lattice.theory.chord import build
    from lattice.theory.pitch import parse_tpc

    segs = tuple(
        Segment(build(parse_tpc(n), "m7"), lbl, i * 4, 4)
        for i, (n, lbl) in enumerate([("A", "i7"), ("D", "iv7"), ("E", "v7"), ("F", "bVI")])
    )
    card = FAIYAZ.override(p_bass_stab=1.0, p_bass_approach=1.0)
    parts = bass_parts(segs, card=card, rng=np.random.default_rng(4))
    for i in range(4):
        collision_tick = i * 4 * 480 + 1680
        events_there = [e for e in parts[Role.BASS] if e.tick == collision_tick]
        assert len(events_there) == 1
        assert events_there[0].vel == 70


def test_walk_clips_to_segment_boundary() -> None:
    card = get_card("ballroom").override(bass_feel="walk")
    segments = (
        Segment(build(-1, "6"), "I6", 0, 3),
        Segment(build(1, "7"), "V7", 3, 5),
    )
    parts = bass_parts(segments, card, np.random.default_rng(2))
    for e in parts[Role.BASS]:
        seg_end = 1440 if e.tick < 1440 else 3840
        assert e.tick + e.dur <= seg_end
