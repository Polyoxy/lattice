from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Final

TPQ: Final = 960


class Role(Enum):
    KEYS = "keys"
    BASS = "bass"
    SUB = "sub"
    KICK = "kick"
    SNARE = "snare"
    HAT = "hat"
    PERC = "perc"
    PAD = "pad"


class DrumSound(Enum):
    KICK = "kick"
    SNARE = "snare"
    RIM = "rim"
    CLAP = "clap"
    HAT_CLOSED = "hat_closed"
    HAT_OPEN = "hat_open"
    RIDE = "ride"
    TOM_LO = "tom_lo"
    TOM_HI = "tom_hi"
    BONGO = "bongo"
    SHAKER = "shaker"
    GHOST_KICK = "ghost_kick"
    BRUSH_TAP = "brush_tap"
    BRUSH_SWIRL = "brush_swirl"
    FEATHER = "feather"
    CHICK = "chick"


@dataclass(frozen=True, slots=True)
class Event:
    tick: int
    dur: int
    vel: int
    pitch: int | None = None
    drum: DrumSound | None = None
    micro_ms: float = 0.0
    glide: bool = False


@dataclass(frozen=True, slots=True)
class Part:
    role: Role
    events: tuple[Event, ...]


@dataclass(frozen=True, slots=True)
class Section:
    kind: str
    cycles: int
    muted: frozenset[Role] = field(default_factory=frozenset)
    transpose: int = 0
    halftime: bool = False
    filter_move: bool = False


@dataclass(frozen=True, slots=True)
class Timeline:
    sections: tuple[Section, ...]

    @property
    def total_cycles(self) -> int:
        return sum(s.cycles for s in self.sections)


def ticks_per_bar() -> int:
    return TPQ * 4


def ms_per_tick(bpm: int) -> float:
    return 60000.0 / (bpm * TPQ)


def bar_s(bpm: int) -> float:
    return 4 * 60.0 / bpm
