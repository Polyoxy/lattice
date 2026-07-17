from __future__ import annotations

from lattice.harmony.elaborate import Segment
from lattice.model import Event
from lattice.theory.pitch import SpelledPitch

_SLOT = 480


def pad_events(
    segments: tuple[Segment, ...],
    voicings: tuple[tuple[SpelledPitch, ...], ...],
    bars: int,
) -> tuple[Event, ...]:
    total = bars * 8 * _SLOT
    events: list[Event] = []
    for j, (seg, stack) in enumerate(zip(segments, voicings, strict=True)):
        start = seg.start_slot * _SLOT
        end = start + seg.dur_slots * _SLOT if j + 1 < len(segments) else total
        pitches = sorted(p.midi for p in stack)[-3:]
        top = max(pitches)
        while top > 86:
            pitches = [p - 12 for p in pitches]
            top -= 12
        while top < 74:
            pitches = [p + 12 for p in pitches]
            top += 12
        events.extend(
            Event(start, end - start, 54, pitch=p) for p in pitches if p >= 55
        )
    return tuple(sorted(events, key=lambda e: (e.tick, e.pitch or 0)))
