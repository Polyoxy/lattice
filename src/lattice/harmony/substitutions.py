from __future__ import annotations

from dataclasses import dataclass

from lattice.cards import StyleCard
from lattice.theory.chord import Chord, build, is_dominant, symbol
from lattice.theory.interval import semitones
from lattice.theory.key import Key
from lattice.theory.pitch import Tpc


@dataclass(frozen=True, slots=True)
class Sub:
    chord: Chord
    label: str


def secondary_dominant(target: Chord) -> Sub:
    return Sub(build(target.root + 1, "7"), f"V7/{symbol(target)}")


def tritone_sub(dom: Chord) -> Sub:
    if not is_dominant(dom):
        raise ValueError(f"not a dominant: {symbol(dom)}")
    return Sub(build(dom.root - 6, "7"), "tritone sub")


def backdoor(key: Key) -> Sub:
    return Sub(build(key.tonic - 2, "7"), "backdoor bVII7")


def related_ii(dom: Chord) -> Sub:
    return Sub(build(dom.root + 1, "m7"), "related ii")


def _semitone_gap(a: Tpc, b: Tpc) -> int:
    return semitones(b - a)


def passing_dim(a: Chord, b: Chord) -> Sub | None:
    if _semitone_gap(a.root, b.root) != 2:
        return None
    return Sub(build(a.root + 7, "dim7"), "passing dim7")


def chromatic_mediants(c: Chord) -> tuple[Sub, Sub]:
    return (
        Sub(build(c.root + 4, "maj7"), "chromatic mediant"),
        Sub(build(c.root - 4, "maj7"), "chromatic mediant"),
    )


def subs_for(card: StyleCard, key: Key, prev: Chord, target: Chord) -> list[Sub]:
    out: list[Sub] = []
    if card.p_kicker > 0:
        sec = secondary_dominant(target)
        out.append(sec)
        if card.allow_tritone_sub:
            out.append(tritone_sub(sec.chord))
        if card.elaboration_density > 0.3:
            out.append(related_ii(sec.chord))
    dim = passing_dim(prev, target)
    if dim is not None and card.elaboration_density > 0.3:
        out.append(dim)
    if card.allow_chromatic_mediant:
        out.extend(chromatic_mediants(target))
    return out
