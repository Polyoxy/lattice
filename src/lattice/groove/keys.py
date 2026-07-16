from __future__ import annotations

import numpy as np

from lattice.cards import StyleCard
from lattice.harmony.elaborate import Segment
from lattice.model import Event
from lattice.theory.pitch import SpelledPitch

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
