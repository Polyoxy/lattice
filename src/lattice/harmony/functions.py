from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from lattice.theory.chord import Chord, build
from lattice.theory.key import Key, Mode

_MINOR_SPECS: Final[dict[str, tuple[int, str, str]]] = {
    "i7": (0, "m7", "i7"),
    "i9": (0, "m9", "i9"),
    "i6add9": (0, "m6add9", "i6/9"),
    "iv7": (-1, "m7", "iv7"),
    "iv9": (-1, "m9", "iv9"),
    "iv6add9": (-1, "m6add9", "iv6/9"),
    "v7": (1, "m7", "v7"),
    "V7": (1, "7", "V7"),
    "V7b9": (1, "7b9", "V7b9"),
    "V7b13": (1, "7b13", "V7b13"),
    "bVImaj7": (-4, "maj7", "bVImaj7"),
    "bIII": (-3, "maj7", "bIIImaj7"),
    "bVII7": (-2, "7", "bVII7"),
    "bVII9": (-2, "9", "bVII9"),
    "ii7": (2, "m7", "ii7 (dorian)"),
    "iim7b5": (2, "m7b5", "ii(m7b5)"),
    "bII": (-5, "maj7", "bIImaj7 (phrygian)"),
    "IV7": (-1, "7", "IV7 (dorian)"),
}
_MAJOR_SPECS: Final[dict[str, tuple[int, str, str]]] = {
    "Imaj7": (0, "maj7", "Imaj7"),
    "ii9": (2, "m9", "ii9"),
    "ii7maj": (2, "m7", "ii7"),
    "iii7": (4, "m7", "iii7"),
    "IVmaj7": (-1, "maj7", "IVmaj7"),
    "V7maj": (1, "7", "V7"),
    "vi7": (3, "m7", "vi7"),
    "vii_m7": (5, "m7", "vii(m7)"),
    "I6": (0, "6", "I6"),
    "I6add9": (0, "6add9", "I6/9"),
    "IV6": (-1, "6", "IV6"),
    "iv6": (-1, "m6", "iv6 (borrowed)"),
    "V9": (1, "9", "V9"),
    "II7": (2, "7", "II7 (V/V)"),
    "III7": (4, "7", "III7 (V/vi)"),
    "VI7": (3, "7", "VI7 (V/ii)"),
    "#idim7": (7, "dim7", "#i dim7"),
}

MINOR_FUNCTIONS: Final = tuple(_MINOR_SPECS)
MAJOR_FUNCTIONS: Final = tuple(_MAJOR_SPECS)


@dataclass(frozen=True, slots=True)
class FunctionChord:
    name: str
    chord: Chord
    roman: str


def _specs(key: Key) -> dict[str, tuple[int, str, str]]:
    return _MAJOR_SPECS if key.mode is Mode.MAJOR else _MINOR_SPECS


def build_function(key: Key, name: str) -> FunctionChord:
    offset, quality, roman = _specs(key)[name]
    return FunctionChord(name, build(key.tonic + offset, quality), roman)


def pool_for(key: Key, names: tuple[str, ...]) -> tuple[str, ...]:
    known = _specs(key)
    return tuple(n for n in names if n in known)
