from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from lattice.cards import StyleCard
from lattice.model import DrumSound, Event, Role

_SWUNG_ROLES = frozenset({Role.HAT, Role.PERC, Role.KEYS, Role.BASS})


@dataclass(frozen=True, slots=True)
class PocketReport:
    swing: float
    snap_ms: float
    clap_ms: float
    sigma_ms: float


def apply_pocket(
    parts: dict[Role, tuple[Event, ...]],
    card: StyleCard,
    bpm: int,
    rng: np.random.Generator,
) -> tuple[dict[Role, tuple[Event, ...]], PocketReport]:
    swing = float(rng.uniform(*card.swing_band))
    snap_ms = float(rng.uniform(*card.snap_rush_ms))
    clap_ms = float(rng.uniform(*card.clap_drag_ms))
    swing_ms = (swing - 0.5) * (60000.0 / bpm)

    out: dict[Role, tuple[Event, ...]] = {}
    for role, events in parts.items():
        new: list[Event] = []
        for e in events:
            micro = e.micro_ms
            if role in _SWUNG_ROLES and e.tick % 960 == 480:
                micro += swing_ms
            if e.drum is DrumSound.SNARE:
                micro += snap_ms
            elif e.drum is DrumSound.CLAP:
                micro += clap_ms
            micro += float(rng.normal(0.0, card.timing_sigma_ms))
            vel = int(np.clip(round(e.vel * (1.0 + rng.normal(0.0, card.vel_jitter))), 1, 127))
            new.append(replace(e, micro_ms=micro, vel=vel))
        out[role] = tuple(new)
    return out, PocketReport(swing, snap_ms, clap_ms, card.timing_sigma_ms)
