from __future__ import annotations

import numpy as np

from lattice.cards import StyleCard
from lattice.model import DrumSound, Event, Role, ticks_per_bar

_KICK_EXTRAS = (1440, 2160, 2640, 3600)
_HIT = 120


def _kick_bar(card: StyleCard, bar: int, rng: np.random.Generator, extra_bias: int) -> list[Event]:
    lo, hi = card.kick_per_bar
    base = bar * ticks_per_bar()
    events = [Event(base, _HIT, int(rng.integers(100, 111)), drum=DrumSound.KICK)]
    n_extra = int(rng.integers(max(0, lo - 1), hi)) + extra_bias
    n_extra = min(n_extra, hi - 1, len(_KICK_EXTRAS))
    for off in rng.choice(len(_KICK_EXTRAS), size=n_extra, replace=False):
        vel = int(rng.integers(88, 104))
        events.append(Event(base + _KICK_EXTRAS[int(off)], _HIT, vel, drum=DrumSound.KICK))
    return events


def _backbeat(bar: int) -> list[Event]:
    t = bar * ticks_per_bar() + 1920
    return [
        Event(t, _HIT, 88, drum=DrumSound.RIM),
        Event(t, _HIT, 68, drum=DrumSound.SNARE),
        Event(t, _HIT, 96, drum=DrumSound.CLAP),
    ]


def _hats(card: StyleCard, bar: int, rng: np.random.Generator, force_roll: bool) -> list[Event]:
    base = bar * ticks_per_bar()
    lo, hi = card.hat_vels
    events = [
        Event(base + i * 480, _HIT, hi if (i * 480) % 960 == 0 else lo, drum=DrumSound.HAT_CLOSED)
        for i in range(8)
    ]
    if force_roll or rng.random() < card.p_hat_roll:
        for i in range(4):
            events.append(Event(base + 2160 + i * 480, _HIT, lo - 10, drum=DrumSound.HAT_CLOSED))
    return events


def _perc(
    card: StyleCard, bar: int, bars: int, rng: np.random.Generator, dense: bool
) -> list[Event]:
    base = bar * ticks_per_bar()
    events: list[Event] = []
    if rng.random() < card.p_perc_bed:
        taken = {0, 1920, *_KICK_EXTRAS}
        n = int(rng.integers(2, 5))
        slots = [t for t in range(0, ticks_per_bar(), 240) if t not in taken]
        for t in rng.choice(len(slots), size=min(n, len(slots)), replace=False):
            sound = DrumSound.SHAKER if rng.random() < 0.6 else DrumSound.BONGO
            events.append(Event(base + slots[int(t)], _HIT, int(rng.integers(30, 51)), drum=sound))
    if bar == bars - 1 and rng.random() < card.p_turnaround:
        n = int(rng.integers(3, 6)) + (1 if dense else 0)
        sounds = (DrumSound.TOM_HI, DrumSound.BONGO, DrumSound.TOM_LO)
        start = base + 2880
        for i in range(min(n, 4)):
            vel = 80 - i * 8
            events.append(Event(start + i * 240, _HIT, vel, drum=sounds[i % 3]))
    return events


def _faiyaz_variant(
    card: StyleCard, bars: int, rng: np.random.Generator, extra_bias: int, force_roll: bool
) -> dict[Role, tuple[Event, ...]]:
    kick: list[Event] = []
    snare: list[Event] = []
    hat: list[Event] = []
    perc: list[Event] = []
    for bar in range(bars):
        kick += _kick_bar(card, bar, rng, extra_bias)
        snare += _backbeat(bar)
        hat += _hats(card, bar, rng, force_roll)
        perc += _perc(card, bar, bars, rng, dense=force_roll)
    return {
        Role.KICK: tuple(kick),
        Role.SNARE: tuple(snare),
        Role.HAT: tuple(hat),
        Role.PERC: tuple(perc),
    }


def faiyaz_patterns(
    card: StyleCard, bars: int, rng: np.random.Generator
) -> dict[str, dict[Role, tuple[Event, ...]]]:
    return {
        "A": _faiyaz_variant(card, bars, rng, extra_bias=0, force_roll=False),
        "B": _faiyaz_variant(card, bars, rng, extra_bias=1, force_roll=True),
    }


def conductor_patterns(
    card: StyleCard, bars: int, rng: np.random.Generator
) -> dict[str, dict[Role, tuple[Event, ...]]]:
    def variant(extra_ghost: bool) -> dict[Role, tuple[Event, ...]]:
        kick: list[Event] = []
        snare: list[Event] = []
        hat: list[Event] = []
        perc: list[Event] = []
        ghost_bars: set[int] = set()
        for bar in range(bars):
            base = bar * ticks_per_bar()
            kick.append(Event(base, _HIT, int(rng.integers(96, 109)), drum=DrumSound.KICK))
            if card.ghost_kicks and rng.random() < 0.5:
                sign = 1 if rng.random() < 0.5 else -1
                t = base + (240 * sign)
                if t >= 0:
                    vel = int(rng.integers(40, 56))
                    kick.append(Event(t, _HIT, vel, drum=DrumSound.GHOST_KICK))
                    ghost_bars.add(bar)
            snare.append(Event(base + 1920, _HIT, int(rng.integers(78, 87)), drum=DrumSound.RIM))
            for q in range(4):
                vel = int(rng.integers(*card.hat_vels))
                hat.append(Event(base + q * 960, _HIT, vel, drum=DrumSound.HAT_CLOSED))
            if bar % 2 == 1:
                sound = DrumSound.HAT_OPEN if rng.random() < 0.5 else DrumSound.RIDE
                hat.append(Event(base + 1440, _HIT, int(rng.integers(55, 75)), drum=sound))
        if extra_ghost and card.ghost_kicks:
            open_bars = [b for b in range(bars) if b not in ghost_bars]
            if open_bars:
                b = open_bars[int(rng.integers(0, len(open_bars)))]
                vel = int(rng.integers(40, 56))
                kick.append(Event(b * ticks_per_bar() + 240, _HIT, vel, drum=DrumSound.GHOST_KICK))
        if rng.random() < card.p_perc_bed:
            perc.append(Event(1200, _HIT, int(rng.integers(30, 45)), drum=DrumSound.SHAKER))
        return {
            Role.KICK: tuple(sorted(kick, key=lambda e: e.tick)),
            Role.SNARE: tuple(snare),
            Role.HAT: tuple(sorted(hat, key=lambda e: e.tick)),
            Role.PERC: tuple(perc),
        }

    return {"A": variant(False), "B": variant(True)}


def ballroom_patterns(
    card: StyleCard, bars: int, rng: np.random.Generator
) -> dict[str, dict[Role, tuple[Event, ...]]]:
    def variant(tap_lift: int) -> dict[Role, tuple[Event, ...]]:
        snare: list[Event] = []
        kick: list[Event] = []
        hat: list[Event] = []
        lo, hi = card.hat_vels
        for bar in range(bars):
            base = bar * ticks_per_bar()
            for t in (960, 2880):
                vel = int(rng.integers(58, 71)) + tap_lift
                snare.append(Event(base + t, _HIT, vel, drum=DrumSound.BRUSH_TAP))
            for t in (0, 1920):
                vel = int(rng.integers(34, 45))
                snare.append(Event(base + t, _HIT, vel, drum=DrumSound.BRUSH_SWIRL))
            for q in range(4):
                vel = int(rng.integers(28, 39))
                kick.append(Event(base + q * 960, _HIT, vel, drum=DrumSound.FEATHER))
            for t in (960, 2880):
                vel = int(rng.integers(lo, hi + 1))
                hat.append(Event(base + t, _HIT, vel, drum=DrumSound.CHICK))
        return {
            Role.KICK: tuple(kick),
            Role.SNARE: tuple(sorted(snare, key=lambda e: e.tick)),
            Role.HAT: tuple(hat),
            Role.PERC: (),
        }

    return {"A": variant(0), "B": variant(8)}
