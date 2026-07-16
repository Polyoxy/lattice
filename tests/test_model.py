from lattice.model import (
    TPQ,
    DrumSound,
    Event,
    Part,
    Role,
    Section,
    Timeline,
    bar_s,
    ms_per_tick,
    ticks_per_bar,
)


def test_grid_constants() -> None:
    assert TPQ == 960
    assert ticks_per_bar() == 3840
    assert abs(ms_per_tick(72) - 60000 / (72 * 960)) < 1e-9
    assert abs(bar_s(72) - 4 * 60 / 72) < 1e-9


def test_event_micro_is_separate_from_grid() -> None:
    e = Event(tick=1920, dur=480, vel=100, drum=DrumSound.CLAP, micro_ms=14.0)
    assert e.tick == 1920 and e.micro_ms == 14.0


def test_timeline_total_cycles() -> None:
    t = Timeline(
        (
            Section("intro", 2, frozenset({Role.KICK, Role.SNARE, Role.HAT, Role.PERC})),
            Section("a", 3, frozenset()),
        )
    )
    assert t.total_cycles == 5


def test_part_is_frozen_tuple_of_events() -> None:
    p = Part(Role.KEYS, (Event(0, 960, 90, pitch=60),))
    assert p.role is Role.KEYS and len(p.events) == 1
