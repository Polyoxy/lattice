from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from lattice.cards import StyleCard
from lattice.harmony.functions import FunctionChord, build_function, pool_for
from lattice.theory.key import Key, Mode

_KICKERS = ("V7", "V7b9", "V7b13")
_MAX_ENUM = 20000


@dataclass(frozen=True, slots=True)
class Loop:
    key: Key
    items: tuple[FunctionChord, ...]
    bars: int

    def names(self) -> tuple[str, ...]:
        return tuple(fc.name for fc in self.items)

    def slots(self) -> tuple[tuple[FunctionChord, int, int], ...]:
        total = self.bars * 8
        base = total // len(self.items)
        out: list[tuple[FunctionChord, int, int]] = []
        start = 0
        for i, fc in enumerate(self.items):
            dur = total - start if i == len(self.items) - 1 else base
            out.append((fc, start, dur))
            start += dur
        return tuple(out)


def _card_pool(card: StyleCard, key: Key) -> tuple[str, ...]:
    names = card.major_function_pool if key.mode is Mode.MAJOR else card.function_pool
    return pool_for(key, names)


def enumerate_progressions(pool: tuple[str, ...], length: int) -> list[tuple[str, ...]]:
    if length == 1:
        return [(n,) for n in pool]
    all_progs = [
        p
        for p in product(pool, repeat=length)
        if all(p[i] != p[i + 1] for i in range(length - 1)) and p[0] != p[-1]
    ]
    if len(all_progs) <= _MAX_ENUM:
        return all_progs
    stride = len(all_progs) // _MAX_ENUM + 1
    return all_progs[::stride]


def candidate_loops(card: StyleCard, key: Key, bars: int) -> list[Loop]:
    pool = _card_pool(card, key)
    seen: set[tuple[str, ...]] = set()
    loops: list[Loop] = []
    for length, _ in card.loop_len_weights:
        for names in enumerate_progressions(pool, length):
            if names in seen:
                continue
            seen.add(names)
            loops.append(Loop(key, tuple(build_function(key, n) for n in names), bars))
    return loops


def expressible(card: StyleCard, key: Key, names: tuple[str, ...]) -> bool:
    pool = set(_card_pool(card, key)) | set(_KICKERS)
    lengths = {ln for ln, _ in card.loop_len_weights}
    return len(names) in lengths and all(n in pool for n in names)
