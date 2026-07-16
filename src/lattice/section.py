from __future__ import annotations

from dataclasses import dataclass

from lattice.harmony.elaborate import Segment
from lattice.harmony.grammar import Loop
from lattice.model import Event, Role
from lattice.theory.pitch import SpelledPitch


@dataclass(frozen=True, slots=True)
class SectionRender:
    loop: Loop
    segments: tuple[Segment, ...]
    voicings: tuple[tuple[SpelledPitch, ...], ...]
    parts_a: dict[Role, tuple[Event, ...]]
    parts_b: dict[Role, tuple[Event, ...]]
