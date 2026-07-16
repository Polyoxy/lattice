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
