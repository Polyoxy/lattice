from __future__ import annotations

from itertools import combinations
from typing import Final

from lattice.cards import StyleCard
from lattice.theory.chord import Chord, is_dominant
from lattice.theory.pitch import SpelledPitch, pitch_class

_LIL_FLOORS: Final[dict[int, int]] = {
    1: 53,
    2: 52,
    3: 48,
    4: 46,
    5: 45,
    6: 44,
    7: 34,
    8: 41,
    9: 39,
    10: 38,
    11: 37,
}


def violates_min9(stack: tuple[SpelledPitch, ...], chord: Chord) -> bool:
    root_pc = pitch_class(chord.root)
    dom = is_dominant(chord)
    for lo, hi in combinations(sorted(stack, key=lambda p: p.midi), 2):
        if (hi.midi - lo.midi) % 12 == 1 and hi.midi != lo.midi:
            if dom and lo.midi % 12 == root_pc:
                continue
            return True
    return False


def violates_lil(stack: tuple[SpelledPitch, ...]) -> bool:
    ordered = sorted(stack, key=lambda p: p.midi)
    for lo, hi in zip(ordered, ordered[1:], strict=False):
        gap = hi.midi - lo.midi
        floor = _LIL_FLOORS.get(gap)
        if floor is not None and lo.midi < floor:
            return True
    return False


def valid(stack: tuple[SpelledPitch, ...], chord: Chord, card: StyleCard) -> bool:
    midis = [p.midi for p in stack]
    if len(set(midis)) != len(midis):
        return False
    if min(midis) < card.register_lo or max(midis) > card.register_hi:
        return False
    if max(midis) - min(midis) > 24:
        return False
    return not violates_min9(stack, chord) and not violates_lil(stack)
