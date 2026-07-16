from __future__ import annotations

import numpy as np

from lattice.cards import StyleCard
from lattice.harmony.elaborate import Segment
from lattice.model import Event, Role
from lattice.theory.pitch import pitch_class

_SLOT = 480


def _sub_pitch(root_tpc: int) -> int:
    pc = pitch_class(root_tpc)
    return min((pc + 12 * o for o in range(0, 5)), key=lambda m: (abs(m - 31), -m))


def bass_parts(
    segments: tuple[Segment, ...], card: StyleCard, rng: np.random.Generator
) -> dict[Role, tuple[Event, ...]]:
    sub_pitches = [_sub_pitch(s.chord.root) for s in segments]
    sub = tuple(
        Event(s.start_slot * _SLOT, s.dur_slots * _SLOT, 92, pitch=p)
        for s, p in zip(segments, sub_pitches, strict=True)
    )
    bass: list[Event] = []
    for i, s in enumerate(segments):
        start = s.start_slot * _SLOT
        root = sub_pitches[i] + 12
        bass.append(Event(start, min(2, s.dur_slots) * _SLOT, 84, pitch=root))
        nxt = sub_pitches[(i + 1) % len(segments)]
        boundary = (s.start_slot + s.dur_slots) * _SLOT
        stab_fires = rng.random() < card.p_bass_stab and s.dur_slots >= 4
        approach_fires = rng.random() < card.p_bass_approach and s.dur_slots >= 2
        if stab_fires:
            bass.append(Event(start + 1440, 240, 72, pitch=root))
            if not (approach_fires and boundary - 240 == start + 1680):
                bass.append(Event(start + 1680, 240, 64, pitch=root))
        if approach_fires:
            glide = bool(rng.random() < card.p_bass_glide)
            bass.append(Event(boundary - 240, 240, 70, pitch=nxt + 12 - 1, glide=glide))
    return {Role.SUB: sub, Role.BASS: tuple(sorted(bass, key=lambda e: e.tick))}
