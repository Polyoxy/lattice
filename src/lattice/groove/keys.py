from __future__ import annotations

import numpy as np

from lattice.cards import StyleCard
from lattice.harmony.elaborate import Segment
from lattice.theory import interval as iv
from lattice.theory.chord import Chord, fifth_interval
from lattice.model import Event
from lattice.theory.pitch import SpelledPitch, pitch_class

_SLOT = 480
_CHOP_OFFSETS = (0, 1440, 2640)
_LH_LO = 40
_LH_HI = 52
_LH_VELS = (92, 74, 84, 74)
_LH_BEAT1_BUMP = 6
_STAB_SLOTS = (3, 6)  # ticks 1440, 2880 within each bar
_STAB_VEL = 68
_STAB_LO = 60
_STAB_HI = 76


def keys_events(
    segments: tuple[Segment, ...],
    voicings: tuple[tuple[SpelledPitch, ...], ...],
    bars: int,
    card: StyleCard,
    rng: np.random.Generator,
    duel_events: tuple[Event, ...] = (),
    avoid_spans: tuple[tuple[int, int], ...] = (),
) -> tuple[Event, ...]:
    total = bars * 8 * _SLOT
    if card.keys_pattern == "stride":
        return _stride(segments, voicings, card, rng)
    if card.keys_pattern == "duel":
        return _duel(segments, voicings, bars, duel_events, avoid_spans)
    if card.keys_pattern == "duel_low":
        return tuple(
            sorted(_duel_lh(segments) + duel_events, key=lambda e: (e.tick, e.pitch or 0))
        )
    if card.keys_reattack == "chop":
        events: list[Event] = []
        for seg, stack in zip(segments, voicings, strict=True):
            seg_start = seg.start_slot * _SLOT
            seg_end = seg_start + seg.dur_slots * _SLOT
            attacks = [seg_start + o for o in _CHOP_OFFSETS if seg_start + o < seg_end]
            for j, t in enumerate(attacks):
                end = attacks[j + 1] if j + 1 < len(attacks) else seg_end
                vel = int(rng.integers(70, 85))
                events.extend(Event(t, end - t, vel, pitch=p.midi) for p in stack)
        return tuple(sorted(events, key=lambda e: (e.tick, e.pitch or 0)))

    attacks = []
    for seg in segments:
        t = seg.start_slot * _SLOT
        if seg.start_slot > 0 and rng.random() < card.p_keys_anticipation:
            t -= 480
        attacks.append(t)
    events = []
    for j, (seg, stack) in enumerate(zip(segments, voicings, strict=True)):
        end = attacks[j + 1] if j + 1 < len(segments) else total
        events.extend(Event(attacks[j], end - attacks[j], 76, pitch=p.midi) for p in stack)
    return tuple(sorted(events, key=lambda e: (e.tick, e.pitch or 0)))


def _nearest_in(pc: int, lo: int, hi: int) -> int:
    candidates = [pc + 12 * o for o in range(11) if lo <= pc + 12 * o <= hi]
    return candidates[0]


def _stride(
    segments: tuple[Segment, ...],
    voicings: tuple[tuple[SpelledPitch, ...], ...],
    card: StyleCard,
    rng: np.random.Generator,
) -> tuple[Event, ...]:
    events: list[Event] = []
    for seg, stack in zip(segments, voicings, strict=True):
        seg_start = seg.start_slot * _SLOT
        seg_end = seg_start + seg.dur_slots * _SLOT
        root_pc = pitch_class(seg.chord.root)
        fifth_pc = pitch_class(seg.chord.root + fifth_interval(seg.chord))
        shifted = _clamp_stack(stack)
        beat_i = 0
        t = ((seg_start + 959) // 960) * 960
        while t < seg_end:
            if (t // 960) % 2 == 0:
                pc = root_pc if beat_i % 2 == 0 else fifth_pc
                events.append(Event(t, 960, 82, pitch=_nearest_in(pc, 40, 55)))
                beat_i += 1
            else:
                onset = t
                if rng.random() < card.p_keys_anticipation:
                    onset = t - 480
                events.extend(Event(onset, 720, 66, pitch=p) for p in shifted)
            t += 960
    return tuple(sorted(events, key=lambda e: (e.tick, e.pitch or 0)))


def _clamp_stack(stack: tuple[SpelledPitch, ...]) -> tuple[int, ...]:
    pitches = [p.midi for p in stack]
    top = max(pitches)
    while top > 76:
        pitches = [p - 12 for p in pitches]
        top -= 12
    while top < 60:
        pitches = [p + 12 for p in pitches]
        top += 12
    return tuple(p for p in pitches if p >= 48)


def _seventh_or_fifth(chord: Chord) -> int:
    # "seventh" per the duel spec means the chord's own m7/M7 token when the chord
    # carries one; anything without a seventh (triads, sus, dim) falls back to the fifth.
    if iv.m7 in chord.intervals:
        return iv.m7
    if iv.M7 in chord.intervals:
        return iv.M7
    return fifth_interval(chord)


def _shift_into(pitches: list[int], lo: int, hi: int) -> tuple[int, ...]:
    top = max(pitches)
    while top > hi:
        pitches = [p - 12 for p in pitches]
        top -= 12
    while top < lo:
        pitches = [p + 12 for p in pitches]
        top += 12
    return tuple(pitches)


def _segment_at(segments: tuple[Segment, ...], slot: int) -> int:
    for i, seg in enumerate(segments):
        if seg.start_slot <= slot < seg.start_slot + seg.dur_slots:
            return i
    return len(segments) - 1


def _duel_lh(segments: tuple[Segment, ...]) -> tuple[Event, ...]:
    events: list[Event] = []
    for seg in segments:
        root_pc = pitch_class(seg.chord.root)
        fifth_pc = pitch_class(seg.chord.root + fifth_interval(seg.chord))
        seventh_pc = pitch_class(seg.chord.root + _seventh_or_fifth(seg.chord))
        cycle = (root_pc, fifth_pc, seventh_pc, fifth_pc)
        for j in range(seg.dur_slots):
            slot = seg.start_slot + j
            vel = _LH_VELS[j % 4] + (_LH_BEAT1_BUMP if slot % 8 == 0 else 0)
            pitch = _nearest_in(cycle[j % 4], _LH_LO, _LH_HI)
            events.append(Event(slot * _SLOT, _SLOT, vel, pitch=pitch))
    return tuple(events)


def _duel_stabs(
    segments: tuple[Segment, ...],
    voicings: tuple[tuple[SpelledPitch, ...], ...],
    bars: int,
    duel_events: tuple[Event, ...],
    avoid_spans: tuple[tuple[int, int], ...] = (),
) -> tuple[Event, ...]:
    events: list[Event] = []
    for bar in range(bars):
        for stab_slot in _STAB_SLOTS:
            slot = bar * 8 + stab_slot
            t = slot * _SLOT
            if any(e.tick < t + _SLOT and t < e.tick + e.dur for e in duel_events):
                continue
            if any(start < t + _SLOT and t < end for start, end in avoid_spans):
                continue
            top2 = sorted(p.midi for p in voicings[_segment_at(segments, slot)])[-2:]
            events.extend(
                Event(t, _SLOT, _STAB_VEL, pitch=p) for p in _shift_into(top2, _STAB_LO, _STAB_HI)
            )
    return tuple(events)


def _duel(
    segments: tuple[Segment, ...],
    voicings: tuple[tuple[SpelledPitch, ...], ...],
    bars: int,
    duel_events: tuple[Event, ...],
    avoid_spans: tuple[tuple[int, int], ...] = (),
) -> tuple[Event, ...]:
    stabs = _duel_stabs(segments, voicings, bars, duel_events, avoid_spans)
    merged = _duel_lh(segments) + stabs + duel_events
    return tuple(sorted(merged, key=lambda e: (e.tick, e.pitch or 0)))
