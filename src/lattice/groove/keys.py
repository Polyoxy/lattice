from __future__ import annotations

import numpy as np

from lattice.cards import StyleCard
from lattice.harmony.elaborate import Segment
from lattice.theory.chord import fifth_interval
from lattice.model import Event
from lattice.theory.pitch import SpelledPitch, pitch_class

_SLOT = 480
_CHOP_OFFSETS = (0, 1440, 2640)


def keys_events(
    segments: tuple[Segment, ...],
    voicings: tuple[tuple[SpelledPitch, ...], ...],
    bars: int,
    card: StyleCard,
    rng: np.random.Generator,
) -> tuple[Event, ...]:
    total = bars * 8 * _SLOT
    if card.keys_pattern == "stride":
        return _stride(segments, voicings, card, rng)
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
