from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from lattice.theory import interval as iv
from lattice.theory.pitch import Tpc, tpc_name

QUALITY_IVS: Final[dict[str, tuple[int, ...]]] = {
    "": (iv.M3, iv.P5),
    "m": (iv.m3, iv.P5),
    "7": (iv.M3, iv.P5, iv.m7),
    "m7": (iv.m3, iv.P5, iv.m7),
    "maj7": (iv.M3, iv.P5, iv.M7),
    "m9": (iv.m3, iv.P5, iv.m7, iv.M9),
    "9": (iv.M3, iv.P5, iv.m7, iv.M9),
    "maj9": (iv.M3, iv.P5, iv.M7, iv.M9),
    "m6add9": (iv.m3, iv.P5, iv.M6, iv.M9),
    "6add9": (iv.M3, iv.P5, iv.M6, iv.M9),
    "add9": (iv.M3, iv.P5, iv.M9),
    "m7b5": (iv.m3, iv.d5, iv.m7),
    "dim": (iv.m3, iv.d5),
    "dim7": (iv.m3, iv.d5, iv.d7),
    "aug": (iv.M3, iv.A5),
    "sus4": (iv.P4, iv.P5),
    "7b9": (iv.M3, iv.P5, iv.m7, iv.m2),
    "7b13": (iv.M3, iv.P5, iv.m7, iv.m6),
    "m11": (iv.m3, iv.P5, iv.m7, iv.M9, iv.P4),
}
_SYMBOL_BY_IVS: Final = {frozenset(v): k for k, v in QUALITY_IVS.items()}


@dataclass(frozen=True, slots=True)
class Chord:
    root: Tpc
    intervals: frozenset[int]
    bass: Tpc | None = None


def build(root: Tpc, quality: str, bass: Tpc | None = None) -> Chord:
    return Chord(root, frozenset(QUALITY_IVS[quality]), bass)


def chord_tpcs(c: Chord) -> tuple[Tpc, ...]:
    return (c.root, *(c.root + i for i in sorted(c.intervals, key=iv.semitones)))


def symbol(c: Chord) -> str:
    q = _SYMBOL_BY_IVS.get(c.intervals)
    name = tpc_name(c.root) + (q if q is not None else "?")
    if c.bass is not None and c.bass != c.root:
        name += "/" + tpc_name(c.bass)
    return name


def is_dominant(c: Chord) -> bool:
    return iv.M3 in c.intervals and iv.m7 in c.intervals
