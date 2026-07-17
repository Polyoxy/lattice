import numpy as np

from lattice import make_beat
from lattice.cards import CONDUCTOR, FAIYAZ, get_card
from lattice.groove.drums import ballroom_patterns, conductor_patterns, faiyaz_patterns
from lattice.model import DrumSound, Role


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def test_composite_backbeat_three_sounds_same_tick() -> None:
    parts = faiyaz_patterns(FAIYAZ, bars=4, rng=_rng(0))["A"]
    snare = parts[Role.SNARE]
    beat3 = [e for e in snare if e.tick == 1920]
    assert {e.drum for e in beat3} == {DrumSound.RIM, DrumSound.SNARE, DrumSound.CLAP}


def test_kick_density_within_band_across_seeds() -> None:
    lo, hi = FAIYAZ.kick_per_bar
    for seed in range(20):
        parts = faiyaz_patterns(FAIYAZ, bars=4, rng=_rng(seed))["A"]
        kicks = parts[Role.KICK]
        for bar in range(4):
            n = sum(1 for e in kicks if bar * 3840 <= e.tick < (bar + 1) * 3840)
            assert lo <= n <= hi


def test_hat_velocities_alternate_pre_pocket() -> None:
    parts = faiyaz_patterns(FAIYAZ, bars=2, rng=_rng(1))["A"]
    hats = [e for e in parts[Role.HAT] if e.tick % 480 == 0]
    for e in hats:
        expected = FAIYAZ.hat_vels[1] if e.tick % 960 == 0 else FAIYAZ.hat_vels[0]
        assert e.vel == expected


def test_all_micro_zero_and_ticks_in_range() -> None:
    for gen, card in ((faiyaz_patterns, FAIYAZ), (conductor_patterns, CONDUCTOR)):
        for variant in gen(card, bars=4, rng=_rng(2)).values():
            for part in variant.values():
                for e in part:
                    assert e.micro_ms == 0.0
                    assert 0 <= e.tick < 4 * 3840


def test_turnaround_lands_last_bar_when_forced() -> None:
    card = FAIYAZ.override(p_turnaround=1.0)
    parts = faiyaz_patterns(card, bars=4, rng=_rng(3))["A"]
    turn_sounds = (DrumSound.TOM_HI, DrumSound.TOM_LO, DrumSound.BONGO)
    toms = [e for e in parts[Role.PERC] if e.drum in turn_sounds]
    assert toms and all(e.tick >= 3 * 3840 + 2880 for e in toms)


def test_conductor_ghost_kick_velocity_band() -> None:
    card = CONDUCTOR.override(ghost_kicks=True)
    found = []
    for seed in range(10):
        parts = conductor_patterns(card, bars=4, rng=_rng(seed))["A"]
        found += [e for e in parts[Role.KICK] if e.drum is DrumSound.GHOST_KICK]
    assert found and all(40 <= e.vel <= 55 for e in found)


def test_conductor_b_variant_guarantees_a_ghost() -> None:
    card = CONDUCTOR.override(ghost_kicks=True)
    for seed in range(10):
        parts = conductor_patterns(card, bars=4, rng=_rng(seed))["B"]
        ghosts = [e for e in parts[Role.KICK] if e.drum is DrumSound.GHOST_KICK]
        assert len(ghosts) >= 1
        assert all(40 <= e.vel <= 55 for e in ghosts)


def test_ballroom_brushes() -> None:
    card = get_card("ballroom")
    patterns = ballroom_patterns(card, 2, np.random.default_rng(5))
    a = patterns["A"]
    taps = [e for e in a[Role.SNARE] if e.drum is DrumSound.BRUSH_TAP]
    assert {e.tick % 3840 for e in taps} <= {960, 2880}
    swirls = [e for e in a[Role.SNARE] if e.drum is DrumSound.BRUSH_SWIRL]
    assert len(swirls) == 4
    feathers = a[Role.KICK]
    assert all(e.drum is DrumSound.FEATHER and e.vel <= 42 for e in feathers)
    assert {e.tick % 960 for e in feathers} == {0}
    chicks = a[Role.HAT]
    assert all(e.drum is DrumSound.CHICK for e in chicks)
    assert {e.tick % 3840 for e in chicks} <= {960, 2880}
    assert a[Role.PERC] == ()


def test_ballroom_b_variant_leans_harder() -> None:
    card = get_card("ballroom")
    patterns = ballroom_patterns(card, 2, np.random.default_rng(5))
    a_taps = [e.vel for e in patterns["A"][Role.SNARE] if e.drum is DrumSound.BRUSH_TAP]
    b_taps = [e.vel for e in patterns["B"][Role.SNARE] if e.drum is DrumSound.BRUSH_TAP]
    assert sum(b_taps) / len(b_taps) > sum(a_taps) / len(a_taps)


def test_ballroom_brush_taps_get_snap_drag() -> None:
    # apply_pocket only recognized DrumSound.SNARE for the snap_rush_ms band, so
    # brush taps (BRUSH_TAP) sailed straight through pocket untouched. With the
    # fix, taps carry the same positive (behind-the-beat) drag as a snare would;
    # dead-mechanism mean would sit near 0 (pure sigma jitter), so >= 3.0 cleanly
    # separates "live" from "dead" for this pinned seed.
    beat = make_beat(style="ballroom", key="F", bpm=112, bars=2, n=1, seed=5)[0]
    taps = [e for e in beat.parts_a[Role.SNARE] if e.drum is DrumSound.BRUSH_TAP]
    assert len(taps) >= 4
    mean_micro = sum(e.micro_ms for e in taps) / len(taps)
    assert mean_micro >= 3.0
