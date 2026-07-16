from __future__ import annotations

from lattice.cards import StyleCard
from lattice.harmony.elaborate import Segment
from lattice.theory.chord import symbol
from lattice.theory.pitch import SpelledPitch
from lattice.voicing.templates import sparseness, stack_candidates

Stack = tuple[SpelledPitch, ...]


def movement(a: Stack, b: Stack) -> float:
    xs = sorted(p.midi for p in a)
    ys = sorted(p.midi for p in b)
    k = min(len(xs), len(ys))
    core = sum(abs(x - y) for x, y in zip(xs[:k], ys[:k], strict=True))
    size_pen = 6 * abs(len(xs) - len(ys))
    top_pen = 2 * max(0, abs(xs[-1] - ys[-1]) - 2)
    return float(core + size_pen + top_pen)


def realize(
    segments: tuple[Segment, ...],
    card: StyleCard,
    bass_covers_root: bool = True,
    seed_from: tuple[SpelledPitch, ...] | None = None,
) -> tuple[Stack, ...]:
    cands = [stack_candidates(s.chord, card, bass_covers_root) for s in segments]
    for s, c in zip(segments, cands, strict=True):
        if not c:
            raise ValueError(f"no valid voicing for {symbol(s.chord)}")
    first_stage = cands[0]
    if seed_from:
        first_stage = sorted(first_stage, key=lambda st: movement(seed_from, st))
    if len(segments) == 1:
        return (first_stage[0],)
    best_cost = float("inf")
    best_path: list[Stack] = []
    for first in first_stage[:8]:
        current: list[tuple[float, list[Stack]]] = [(sparseness(len(first), card), [first])]
        for stage in cands[1:]:
            nxt: list[tuple[float, list[Stack]]] = []
            for cost, path in current:
                for cand in stage:
                    step = movement(path[-1], cand) + sparseness(len(cand), card)
                    nxt.append((cost + step, [*path, cand]))
            nxt.sort(key=lambda t: t[0])
            current = nxt[:24]
        for cost, path in current:
            total = cost + movement(path[-1], first)
            if total < best_cost:
                best_cost = total
                best_path = path
    return tuple(best_path)
