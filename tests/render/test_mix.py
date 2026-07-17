import wave
from pathlib import Path

import numpy as np
import pytest

from lattice import make_beat
from lattice.model import Role
from lattice.render.kits import load_kit
from lattice.render.mix import MIX_TABLE, render_mix
from lattice.render.stems import render_role_stem
from lattice.render.timing import total_seconds


def _rms(path: Path) -> float:
    with wave.open(str(path)) as w:
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return float(np.sqrt(np.mean((data / 32768.0) ** 2)))


def _peak(path: Path) -> float:
    with wave.open(str(path)) as w:
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return float(np.max(np.abs(data / 32768.0)))


def test_mix_renders_nonsilent_correct_duration(tmp_path: Path) -> None:
    try:
        kit = load_kit()
    except FileNotFoundError:
        pytest.skip("kit not fetched")
    beat = make_beat(style="faiyaz", key="Am", bpm=90, bars=2, n=1, seed=3)[0]
    stems: dict[Role, Path] = {}
    for role in Role:
        p = render_role_stem(beat, role, tmp_path / f"{role.value}.wav", kit=kit)
        if p.exists():
            stems[role] = p
    out = render_mix(beat, stems, tmp_path / "mix.wav")
    assert out.exists()
    with wave.open(str(out)) as w:
        assert abs(w.getnframes() / w.getframerate() - total_seconds(beat)) < 0.2
    assert _rms(out) > 1e-4


def test_hot_mix_stays_under_limiter_ceiling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    try:
        kit = load_kit()
    except FileNotFoundError:
        pytest.skip("kit not fetched")
    beat = make_beat(style="faiyaz", key="Am", bpm=90, bars=2, n=1, seed=3)[0]
    stems: dict[Role, Path] = {}
    for role in Role:
        p = render_role_stem(beat, role, tmp_path / f"{role.value}.wav", kit=kit)
        if p.exists():
            stems[role] = p
    hot_rows = {
        role: (gain_db + 12.0, pan, mono)
        for role, (gain_db, pan, mono) in MIX_TABLE["faiyaz"].items()
    }
    monkeypatch.setitem(MIX_TABLE, "faiyaz", hot_rows)
    out = render_mix(beat, stems, tmp_path / "hot_mix.wav")
    assert _peak(out) <= 0.96
