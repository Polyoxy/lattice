import time

from lattice import Beat, make_beat
from lattice.model import Role
from lattice.theory.key import parse_key


def test_returns_n_distinct_reproducible_beats() -> None:
    a = make_beat(style="faiyaz", key="C#m", bpm=72, bars=4, n=3, seed=7)
    b = make_beat(style="faiyaz", key="C#m", bpm=72, bars=4, n=3, seed=7)
    assert len(a) == 3 and all(isinstance(x, Beat) for x in a)
    assert [x.to_json() for x in a] == [x.to_json() for x in b]
    assert len({x.loop.names() for x in a}) == 3


def test_different_seeds_differ() -> None:
    a = make_beat(key="Am", bpm=72, n=1, seed=1)[0]
    b = make_beat(key="Am", bpm=72, n=1, seed=2)[0]
    assert a.to_json() != b.to_json()


def test_key_and_bpm_defaults_come_from_card() -> None:
    beats = make_beat(style="faiyaz", n=4, seed=3)
    for x in beats:
        assert 65 <= x.bpm <= 95
    assert make_beat(key="Gm", n=1, seed=0)[0].key == parse_key("Gm")


def test_drumless_roll_empties_drums() -> None:
    from lattice.cards import FAIYAZ

    card = FAIYAZ.override(p_drumless=1.0)
    x = make_beat(style=card, key="Am", bpm=72, n=1, seed=0)[0]
    for role in (Role.KICK, Role.SNARE, Role.HAT, Role.PERC):
        assert x.parts_a[role] == ()


def test_molina_elaborates_and_runs_end_to_end() -> None:
    x = make_beat(style="molina", key="Cm", bpm=80, n=1, seed=5)[0]
    assert len(x.segments) >= len(x.loop.items)
    assert x.explain()


def test_speed_budget_for_five_beats() -> None:
    t0 = time.monotonic()
    make_beat(style="faiyaz", key="Am", bpm=72, bars=4, n=5, seed=11)
    assert time.monotonic() - t0 < 30.0


def test_empty_length_pool_fails_fast() -> None:
    import pytest

    from lattice.cards import FAIYAZ

    card = FAIYAZ.override(loop_len_weights=((4, 1.0),), function_pool=("i7",))
    with pytest.raises(ValueError, match="no loops of length 4"):
        make_beat(style=card, key="Am", bpm=72, n=1, seed=0)


def test_bpm_below_minimum_rejected() -> None:
    import pytest

    with pytest.raises(ValueError, match="bpm must be >= 20"):
        make_beat(key="Am", bpm=10, n=1, seed=0)


def test_bars_below_minimum_rejected() -> None:
    import pytest

    with pytest.raises(ValueError, match="bars must be >= 1"):
        make_beat(key="Am", bpm=72, bars=0, n=1, seed=0)


def test_chase_lead_answers_reach_main_a_sections() -> None:
    # Main-section conversation answers alternate PAD and LEAD, so the violin's answer
    # stream exists in parts_a itself (pre-muting; bars=4 gives the two spans round-robin
    # needs to reach LEAD). The entrance assertion — LEAD silent in body sections before
    # lead_enters_section — lands in Task 8, which wires that muting in arrange.
    beat = make_beat(style="chase", key="Dm", bpm=160, bars=4, n=1, seed=5)[0]
    assert beat.parts_a[Role.LEAD]
    unrolled = beat.unrolled()[Role.LEAD]
    assert unrolled
    cycle_ticks = beat.bars * 3840
    a_ranges = []
    cycle = 0
    for s in beat.timeline.sections:
        if s.kind == "a":
            a_ranges.append((cycle * cycle_ticks, (cycle + s.cycles) * cycle_ticks))
        cycle += s.cycles
    assert a_ranges
    assert any(lo <= e.tick < hi for e in unrolled for lo, hi in a_ranges)
