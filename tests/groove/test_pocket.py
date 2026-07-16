import numpy as np

from lattice.cards import FAIYAZ
from lattice.groove.pocket import apply_pocket
from lattice.model import DrumSound, Event, Role


def _parts() -> dict[Role, tuple[Event, ...]]:
    hats = tuple(Event(i * 480, 120, 80, drum=DrumSound.HAT_CLOSED) for i in range(8))
    backbeat = (
        Event(1920, 120, 88, drum=DrumSound.RIM),
        Event(1920, 120, 68, drum=DrumSound.SNARE),
        Event(1920, 120, 96, drum=DrumSound.CLAP),
    )
    return {Role.HAT: hats, Role.SNARE: backbeat}


def test_ticks_never_change_and_input_unmodified() -> None:
    parts = _parts()
    out, _ = apply_pocket(parts, FAIYAZ, bpm=72, rng=np.random.default_rng(0))
    assert [e.tick for e in out[Role.HAT]] == [e.tick for e in parts[Role.HAT]]
    assert all(e.micro_ms == 0.0 for e in parts[Role.HAT])


def test_snap_rushes_and_clap_drags_within_bands() -> None:
    sigma = FAIYAZ.timing_sigma_ms
    for seed in range(10):
        out, report = apply_pocket(_parts(), FAIYAZ, bpm=72, rng=np.random.default_rng(seed))
        by_drum = {e.drum: e for e in out[Role.SNARE]}
        snap = by_drum[DrumSound.SNARE]
        clap = by_drum[DrumSound.CLAP]
        assert -20 - 4 * sigma <= snap.micro_ms <= -10 + 4 * sigma
        assert 10 - 4 * sigma <= clap.micro_ms <= 20 + 4 * sigma
        assert report.snap_ms <= 0 <= report.clap_ms


def test_swing_delays_off_eighths_on_average() -> None:
    out, report = apply_pocket(_parts(), FAIYAZ, bpm=72, rng=np.random.default_rng(1))
    off = [e.micro_ms for e in out[Role.HAT] if e.tick % 960 == 480]
    on = [e.micro_ms for e in out[Role.HAT] if e.tick % 960 == 0]
    expected = (report.swing - 0.5) * (60000 / 72)
    assert abs(float(np.mean(off)) - float(np.mean(on)) - expected) < 3 * FAIYAZ.timing_sigma_ms


def test_velocities_clipped_and_deterministic() -> None:
    a, _ = apply_pocket(_parts(), FAIYAZ, bpm=72, rng=np.random.default_rng(5))
    b, _ = apply_pocket(_parts(), FAIYAZ, bpm=72, rng=np.random.default_rng(5))
    assert a == b
    for part in a.values():
        assert all(1 <= e.vel <= 127 for e in part)
