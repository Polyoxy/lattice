import numpy as np

from lattice.cards import CONDUCTOR, FAIYAZ
from lattice.groove.drums import conductor_patterns, faiyaz_patterns
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
