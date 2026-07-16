from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from lattice.theory.pitch import Tpc, parse_tpc, tpc_name


class Mode(Enum):
    MAJOR = "major"
    AEOLIAN = "aeolian"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"


@dataclass(frozen=True, slots=True)
class Key:
    tonic: Tpc
    mode: Mode


def parse_key(s: str) -> Key:
    if s.endswith("m"):
        return Key(parse_tpc(s[:-1]), Mode.AEOLIAN)
    return Key(parse_tpc(s), Mode.MAJOR)


def key_name(k: Key) -> str:
    return tpc_name(k.tonic) + ("m" if k.mode is not Mode.MAJOR else "")
