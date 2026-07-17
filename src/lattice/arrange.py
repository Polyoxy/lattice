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
    kinds = [c for c in card.section_pattern.lower() if c in ("a", "b")] or ["a", "b"]
    i = 0
    drop_pending = rng.random() < 0.5
    while remaining > 0:
        kind = kinds[i % len(kinds)]
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
    if card.has_bridge and not any(s.kind == "b" for s in sections):
        for j in range(len(sections) - 1, -1, -1):
            if sections[j].kind == "a":
                s = sections[j]
                sections[j] = Section("b", s.cycles, s.muted, s.transpose)
                break
    sections.append(Section("outro", 1, _ALL_BUT_KEYS))
    if rng.random() < card.p_transpose_event:
        idx = max((j for j, s in enumerate(sections) if s.kind in ("a", "b")), default=None)
        if idx is not None:
            for j in range(idx, len(sections)):
                s = sections[j]
                sections[j] = Section(
                    s.kind, s.cycles, s.muted, transpose=card.transpose_semitones
                )
    if card.pad_enters_section:
        body_i = 0
        for j, s in enumerate(sections):
            if s.kind in ("intro", "outro"):
                continue
            body_i += 1
            if body_i < card.pad_enters_section:
                sections[j] = Section(
                    s.kind, s.cycles, s.muted | {Role.PAD}, s.transpose
                )
    return Timeline(tuple(sections))
