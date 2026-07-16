import numpy as np

from lattice.cards import FAIYAZ
from lattice.groove.drums import faiyaz_patterns
from lattice.groove.pocket import apply_pocket
from lattice.model import DrumSound, Role


def test_micro_timing_distributions_over_100_seeds() -> None:
    snaps: list[float] = []
    claps: list[float] = []
    kick_counts: list[int] = []
    on_vels: list[int] = []
    off_vels: list[int] = []
    for seed in range(100):
        rng = np.random.default_rng(seed)
        raw = faiyaz_patterns(FAIYAZ, bars=4, rng=rng)["A"]
        parts, _ = apply_pocket(raw, FAIYAZ, bpm=72, rng=np.random.default_rng(seed + 10_000))
        for e in parts[Role.SNARE]:
            if e.drum is DrumSound.SNARE:
                snaps.append(e.micro_ms)
            elif e.drum is DrumSound.CLAP:
                claps.append(e.micro_ms)
        for bar in range(4):
            kick_counts.append(
                sum(1 for e in parts[Role.KICK] if bar * 3840 <= e.tick < (bar + 1) * 3840)
            )
        for e in parts[Role.HAT]:
            if e.tick % 480 == 0:
                (on_vels if e.tick % 960 == 0 else off_vels).append(e.vel)

    assert -20 <= float(np.mean(snaps)) <= -10
    assert 10 <= float(np.mean(claps)) <= 20
    lo, hi = FAIYAZ.kick_per_bar
    assert min(kick_counts) >= lo and max(kick_counts) <= hi
    assert float(np.mean(on_vels)) > float(np.mean(off_vels))
