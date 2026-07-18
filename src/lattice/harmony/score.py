from __future__ import annotations

from functools import lru_cache
from itertools import permutations
from typing import Final

from lattice.cards import StyleCard
from lattice.harmony.grammar import Loop
from lattice.theory.chord import Chord, is_dominant
from lattice.theory.key import Key
from lattice.theory.pitch import pitch_class

W_VL: Final = 0.6
W_IDIOM: Final = 6.0
W_TONIC: Final = 2.0
W_ARC: Final = 1.0
W_COLOR: Final = 0.5


def canonical_rotation(names: tuple[str, ...]) -> tuple[str, ...]:
    rotations = [names[i:] + names[:i] for i in range(len(names))]
    return min(rotations)


_RAW_IDIOM_SHAPES: Final[frozenset[tuple[str, ...]]] = frozenset(
    {
        ("bVImaj7", "i7"),
        ("bVImaj7", "v7"),
        ("i7", "v7"),
        ("i7", "V7"),
        ("iv7", "v7", "i7", "bVImaj7"),
        ("iv6add9", "v7", "i7", "bVImaj7"),
        ("i7", "bVImaj7", "iv7"),
        ("i7", "bII"),
        ("i7", "ii7", "v7"),
        ("i7", "iv7", "V7b13"),
        ("iv7", "v7", "bVImaj7"),
        ("i7", "v7", "V7"),
        ("ii9", "V7maj", "Imaj7", "vi7"),
        ("Imaj7", "vii_m7"),
        ("i7", "IV7", "iv7"),
        ("iv7", "i7", "bVImaj7", "V7"),
        ("i7", "ii7", "V7", "bVImaj7"),
        ("i9",),
        ("I6", "vi7", "ii7maj", "V7maj"),
        ("I6", "#idim7", "ii7maj", "V7maj"),
        ("iii7", "VI7", "ii7maj", "V7maj"),
        ("I6", "iv6"),
        ("III7", "VI7", "II7", "V7maj"),
        ("I6", "II7", "ii7maj", "V7maj"),
    }
)

IDIOM_SHAPES: Final[frozenset[tuple[str, ...]]] = frozenset(
    canonical_rotation(s) for s in _RAW_IDIOM_SHAPES
)

CARD_IDIOM_SHAPES: Final[dict[str, frozenset[tuple[str, ...]]]] = {
    "chase": frozenset(
        canonical_rotation(s)
        for s in (
            ("i7", "bVII7", "bVImaj7", "V7"),
            ("i7", "bVII7", "bVImaj7", "V7b9"),
            ("i9", "iim7b5", "V7b9"),
            ("i7", "iv9", "bVII7", "bVImaj7"),
        )
    ),
}

_TONIC_NAMES: Final = frozenset({"i7", "i9", "i6add9", "Imaj7", "I6", "I6add9"})
_SUBDOM_DOM: Final = frozenset({"iv7", "iv9", "iv6add9", "v7", "V7", "V7b9", "V7b13", "bVImaj7"})


def tension(c: Chord, key: Key) -> float:
    alt = sum(1 for i in c.intervals if i in (-5, -4, -6, 8, -9))
    size = len(c.intervals)
    fifths_dist = abs(c.root - key.tonic)
    return alt * 2.0 + size * 0.3 + fifths_dist * 0.25


def vl_distance(a: Chord, b: Chord) -> int:
    return _vl_cached(b.root - a.root, a.intervals, b.intervals)


@lru_cache(maxsize=None)
def _vl_cached(root_delta: int, ivs_a: frozenset[int], ivs_b: frozenset[int]) -> int:
    pcs_a = [pitch_class(t) for t in (0, *ivs_a)]
    pcs_b = [pitch_class(root_delta + t) for t in (0, *ivs_b)]
    small, big = sorted((pcs_a, pcs_b), key=len)
    best = 10**9
    for perm in permutations(big, len(small)):
        cost = 0
        for x, y in zip(small, perm, strict=True):
            d = abs(x - y) % 12
            cost += min(d, 12 - d)
        best = min(best, cost)
    return best


def _arc_fit(loop: Loop, key: Key) -> float:
    tensions = [tension(fc.chord, key) for fc in loop.items]
    if len(tensions) == 1:
        return 0.0
    peak_last = tensions[-1] >= max(tensions[:-1])
    resolves = tensions[0] <= tensions[-1]
    return (1.0 if peak_last else 0.0) + (0.5 if resolves else 0.0)


def loop_score(loop: Loop, card: StyleCard) -> float:
    names = loop.names()
    vl_total = sum(
        vl_distance(loop.items[i].chord, loop.items[(i + 1) % len(loop.items)].chord)
        for i in range(len(loop.items))
    )
    vl_term = -W_VL * vl_total / len(loop.items)
    canonical = canonical_rotation(names)
    card_shapes = CARD_IDIOM_SHAPES.get(card.name, frozenset())
    idiom = W_IDIOM if canonical in IDIOM_SHAPES or canonical in card_shapes else 0.0
    has_tonic = bool(_TONIC_NAMES & set(names))
    avoid_ok = len(_SUBDOM_DOM & set(names)) >= 2
    tonic_term = W_TONIC if has_tonic else (W_TONIC * card.p_tonic_avoid if avoid_ok else -W_TONIC)
    arc = W_ARC * _arc_fit(loop, loop.key)
    color = W_COLOR * (sum(len(fc.chord.intervals) for fc in loop.items) / len(loop.items) - 3.0)
    return vl_term + idiom + tonic_term + arc + color


def _root_motion_signature(loop: Loop) -> tuple[int, ...]:
    roots = [fc.chord.root for fc in loop.items]
    return tuple(
        pitch_class(roots[(i + 1) % len(roots)] - roots[i]) for i in range(len(roots))
    )


def contrast(a: Loop, b: Loop) -> float:
    score = 0.0
    if _root_motion_signature(a) != _root_motion_signature(b):
        score += 2.0
    if is_dominant(b.items[-1].chord):
        score += 1.5
    if len(a.items) != len(b.items):
        score += 0.5
    return score


def rank(loops: list[Loop], card: StyleCard, n: int) -> list[Loop]:
    scored = sorted(loops, key=lambda lp: loop_score(lp, card), reverse=True)
    out: list[Loop] = []
    seen_sigs: set[tuple[tuple[int, ...], int]] = set()
    for lp in scored:
        sig = (_root_motion_signature(lp), len(lp.items))
        if sig in seen_sigs:
            continue
        seen_sigs.add(sig)
        out.append(lp)
        if len(out) == n:
            break
    chosen = set(out)
    for lp in scored:
        if len(out) == n:
            break
        if lp not in chosen:
            out.append(lp)
            chosen.add(lp)
    return out[:n]
