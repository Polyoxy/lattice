from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from lattice.cards import StyleCard
from lattice.harmony.grammar import Loop
from lattice.harmony.score import vl_distance
from lattice.harmony.substitutions import Sub, subs_for
from lattice.theory.chord import Chord
from lattice.theory.interval import semitones

_BEAM_WIDTH = 100


@dataclass(frozen=True, slots=True)
class Segment:
    chord: Chord
    label: str
    start_slot: int
    dur_slots: int


def _resolves(sub: Chord, target: Chord) -> bool:
    delta = target.root - sub.root
    return delta == -1 or semitones(delta) in (1, 11)


def _bar_change_counts(segments: tuple[Segment, ...], bars: int) -> list[int]:
    counts = [0] * bars
    for s in segments:
        counts[s.start_slot // 8] += 1
    return counts


def elaborate(loop: Loop, card: StyleCard, rng: np.random.Generator) -> tuple[Segment, ...]:
    base = loop.slots()
    window = 2 if card.elaboration_density > 0.5 else 1
    change_penalty = 2.0 * (1.0 - card.elaboration_density)
    approach_bonus = 4.0 * card.elaboration_density
    n = len(base)

    paths: list[tuple[float, list[Segment]]] = [(0.0, [])]
    for i, (fc, start, dur) in enumerate(base):
        nxt = base[(i + 1) % n][0]
        options: list[tuple[Sub | None, int]] = [(None, 0)]
        if dur > window:
            for candidate in subs_for(card, loop.key, fc.chord, nxt.chord):
                options.append((candidate, window))
        new_paths: list[tuple[float, list[Segment]]] = []
        for score, segs in paths:
            for ins, w in options:
                cand = list(segs)
                cand.append(Segment(fc.chord, fc.roman, start, dur - w))
                s = score
                if ins is not None:
                    cand.append(Segment(ins.chord, ins.label, start + dur - w, w))
                    s -= 0.5 * (
                        vl_distance(fc.chord, ins.chord) + vl_distance(ins.chord, nxt.chord)
                    )
                    s -= change_penalty
                    if _resolves(ins.chord, nxt.chord):
                        s += approach_bonus
                else:
                    s -= 0.5 * vl_distance(fc.chord, nxt.chord)
                new_paths.append((s, cand))
        order = rng.permutation(len(new_paths))
        shuffled = [new_paths[int(j)] for j in order]
        shuffled.sort(key=lambda p: p[0], reverse=True)
        paths = shuffled[:_BEAM_WIDTH]

    for _, segs in paths:
        counts = _bar_change_counts(tuple(segs), loop.bars)
        if max(counts) <= card.max_changes_per_bar:
            return tuple(segs)
    return tuple(paths[0][1])
