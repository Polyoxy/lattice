from __future__ import annotations

from dataclasses import dataclass
from typing import Final

Tpc = int

LETTERS: Final = "CDEFGAB"
LETTER_SEMITONES: Final = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
LETTER_TPC: Final = {"C": 0, "D": 2, "E": 4, "F": -1, "G": 1, "A": 3, "B": 5}


def pitch_class(tpc: Tpc) -> int:
    return (tpc * 7) % 12


def letter(tpc: Tpc) -> str:
    return LETTERS[(tpc * 4) % 7]


def alteration(tpc: Tpc) -> int:
    return (tpc + 1) // 7


def _accidental(alt: int) -> str:
    if alt >= 0:
        return "x" * (alt // 2) + "#" * (alt % 2)
    return "b" * -alt


def tpc_name(tpc: Tpc) -> str:
    return letter(tpc) + _accidental(alteration(tpc))


def parse_tpc(name: str) -> Tpc:
    if not name or name[0].upper() not in LETTER_TPC:
        raise ValueError(f"bad pitch name: {name!r}")
    base = LETTER_TPC[name[0].upper()]
    rest = name[1:]
    if set(rest) - set("#bx"):
        raise ValueError(f"bad accidentals: {name!r}")
    return base + 7 * (rest.count("#") + 2 * rest.count("x") - rest.count("b"))


def same_pitch_class(a: Tpc, b: Tpc) -> bool:
    return (a - b) % 12 == 0


@dataclass(frozen=True, slots=True)
class SpelledPitch:
    tpc: Tpc
    octave: int

    @property
    def midi(self) -> int:
        return 12 * (self.octave + 1) + LETTER_SEMITONES[letter(self.tpc)] + alteration(self.tpc)

    def name(self) -> str:
        return f"{tpc_name(self.tpc)}{self.octave}"


def parse_pitch(s: str) -> SpelledPitch:
    i = len(s)
    while i > 0 and (s[i - 1].isdigit() or s[i - 1] == "-"):
        i -= 1
    if i == len(s):
        raise ValueError(f"missing octave: {s!r}")
    return SpelledPitch(parse_tpc(s[:i]), int(s[i:]))
