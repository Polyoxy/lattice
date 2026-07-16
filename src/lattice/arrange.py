from __future__ import annotations

import numpy as np

from lattice.cards import StyleCard
from lattice.model import Role, Section, Timeline, bar_s

_ALL_BUT_KEYS = frozenset(r for r in Role if r is not Role.KEYS)
_DRUMS = frozenset({Role.KICK, Role.SNARE, Role.HAT, Role.PERC})


def build_timeline(
    card: StyleCard, bars: int, bpm: int, rng: np.random.Generator
) -> Timeline:
    cycle_s = bars * bar_s(bpm)
    target = float(rng.uniform(*card.target_len_s))
    n_cycles = int(np.clip(round(target / cycle_s), 4, 24))

    sections: list[Section] = [Section("intro", 1, _ALL_BUT_KEYS)]
    remaining = n_cycles - 2
    kinds = ["a", "b"]
    i = 0
    drop_pending = rng.random() < 0.5
    while remaining > 0:
        kind = kinds[i % 2]
        max_val = int(rng.integers(2, 4))
        cycles = min(remaining, max_val)
        sections.append(Section(kind, cycles))
        remaining -= cycles
        if kind == "b" and drop_pending and remaining > 0:
            muted = frozenset({Role.HAT}) if rng.random() < 0.5 else _DRUMS
            sections.append(Section("drop", 1, muted))
            remaining -= 1
            drop_pending = False
        i += 1
    if rng.random() < card.p_transpose_event:
        for idx in range(len(sections) - 1, -1, -1):
            if sections[idx].kind in ("a", "b"):
                s = sections[idx]
                sections[idx] = Section(
                    s.kind, s.cycles, s.muted, transpose=card.transpose_semitones
                )
                break
    sections.append(Section("outro", 1, _ALL_BUT_KEYS))
    return Timeline(tuple(sections))
