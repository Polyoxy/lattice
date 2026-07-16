import numpy as np

from lattice.cards import FAIYAZ, MOLINA
from lattice.harmony.elaborate import elaborate
from lattice.harmony.functions import build_function
from lattice.harmony.grammar import Loop
from lattice.theory.key import parse_key


def _loop(key_s: str, names: tuple[str, ...], bars: int = 4) -> Loop:
    k = parse_key(key_s)
    return Loop(k, tuple(build_function(k, n) for n in names), bars)


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def test_segments_tile_grid_exactly() -> None:
    segs = elaborate(_loop("Am", ("i7", "v7")), FAIYAZ, _rng(0))
    assert segs[0].start_slot == 0
    assert sum(s.dur_slots for s in segs) == 32
    for a, b in zip(segs, segs[1:], strict=False):
        assert a.start_slot + a.dur_slots == b.start_slot


def test_faiyaz_respects_max_changes_per_bar() -> None:
    for seed in range(10):
        segs = elaborate(_loop("Gm", ("i7", "iv7", "v7")), FAIYAZ, _rng(seed))
        starts_per_bar: dict[int, int] = {}
        for s in segs:
            starts_per_bar[s.start_slot // 8] = starts_per_bar.get(s.start_slot // 8, 0) + 1
        assert max(starts_per_bar.values()) <= FAIYAZ.max_changes_per_bar


def test_molina_inserts_approach_chords() -> None:
    inserted = 0
    for seed in range(10):
        segs = elaborate(_loop("Cm", ("i7", "iv7"), bars=4), MOLINA, _rng(seed))
        inserted += sum(1 for s in segs if s.label not in ("i7", "iv7"))
    assert inserted >= 5


def test_base_chords_keep_their_start_slots() -> None:
    loop = _loop("Bm", ("iv7", "v7", "i7", "bVImaj7"))
    segs = elaborate(loop, MOLINA, _rng(3))
    base_starts = {start for _, start, _ in loop.slots()}
    seg_starts = {s.start_slot for s in segs}
    assert base_starts <= seg_starts


def test_deterministic_per_seed() -> None:
    a = elaborate(_loop("Am", ("i7", "v7")), MOLINA, _rng(7))
    b = elaborate(_loop("Am", ("i7", "v7")), MOLINA, _rng(7))
    assert a == b


def test_molina_insert_mix_is_pinned() -> None:
    from collections import Counter

    from lattice.cards import MOLINA
    from lattice.harmony.functions import build_function
    from lattice.harmony.grammar import Loop
    from lattice.theory.key import parse_key

    kinds: Counter[str] = Counter()
    key = parse_key("Cm")
    loop = Loop(key, tuple(build_function(key, n) for n in ("i7", "iv7", "v7")), bars=4)
    for seed in range(40):
        segs = elaborate(loop, MOLINA, _rng(seed))
        for s in segs:
            if s.label.startswith("V7/"):
                kinds["secondary"] += 1
            elif "tritone" in s.label:
                kinds["tritone"] += 1
            elif s.label not in ("i7", "iv7", "v7"):
                kinds["other"] += 1
    assert kinds["secondary"] > 0
    assert kinds["other"] == 0
