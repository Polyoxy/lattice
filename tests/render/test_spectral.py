import wave
from pathlib import Path

import numpy as np
import pytest

from lattice import make_beat
from lattice.model import Role
from lattice.render.engine import render_beat
from lattice.render.kits import load_kit

pytestmark = pytest.mark.slow


def _read(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path)) as w:
        rate = w.getframerate()
        channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if sampwidth == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        ints = (
            b[:, 0].astype(np.int32)
            | (b[:, 1].astype(np.int32) << 8)
            | (b[:, 2].astype(np.int32) << 16)
        )
        ints = np.where(ints >= 2**23, ints - 2**24, ints)
        data = ints.astype(np.float64) / float(2**23)
    else:
        data = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if channels == 2:
        data = data.reshape(-1, 2)
    return data, rate


def band_energy(mono: np.ndarray, rate: int, lo: float, hi: float) -> float:
    spectrum = np.abs(np.fft.rfft(mono))
    freqs = np.fft.rfftfreq(len(mono), 1 / rate)
    mask = (freqs >= lo) & (freqs < hi)
    return float(spectrum[mask].mean())


def _render(style: str, seed: int, tmp: Path):  # type: ignore[no-untyped-def]
    try:
        load_kit()
    except FileNotFoundError:
        pytest.skip("kit not fetched")
    beat = make_beat(style=style, key="Am", bpm=88, bars=2, n=1, seed=seed)[0]
    return render_beat(beat, tmp)


def test_faiyaz_master_is_dark_above_16k(tmp_path: Path) -> None:
    result = _render("faiyaz", 3, tmp_path)
    data, rate = _read(result.master)
    mono = data.mean(axis=1)
    assert band_energy(mono, rate, 17000, 21000) < band_energy(mono, rate, 1000, 5000) * 0.05


def test_conductor_master_is_dark_and_duller_than_faiyaz(tmp_path: Path) -> None:
    cond = _render("conductor", 5, tmp_path / "c")
    fai = _render("faiyaz", 5, tmp_path / "f")
    c_data, c_rate = _read(cond.master)
    f_data, f_rate = _read(fai.master)
    c_ratio = band_energy(c_data.mean(axis=1), c_rate, 10000, 15000) / band_energy(
        c_data.mean(axis=1), c_rate, 500, 2000
    )
    f_ratio = band_energy(f_data.mean(axis=1), f_rate, 10000, 15000) / band_energy(
        f_data.mean(axis=1), f_rate, 500, 2000
    )
    assert c_ratio < 0.02
    assert c_ratio < f_ratio


def test_bass_stem_is_mono(tmp_path: Path) -> None:
    result = _render("faiyaz", 3, tmp_path)
    if Role.BASS not in result.stems:
        pytest.skip("no bass stem")
    data, _ = _read(result.stems[Role.BASS])
    corr = float(np.corrcoef(data[:, 0], data[:, 1])[0, 1])
    assert corr > 0.99


def test_master_leaves_headroom(tmp_path: Path) -> None:
    result = _render("faiyaz", 3, tmp_path)
    data, _ = _read(result.master)
    assert 0.5 < float(np.abs(data).max()) <= 1.0


def test_molina_fluidsynth_keys_hold_level_against_scsynth(tmp_path: Path) -> None:
    # fluidsynth's default master gain left the piano ~20dB under the scsynth
    # stems; measured at the calibrated gain: molina mid/low 0.089, faiyaz 0.077,
    # broken state 0.032 with keys stem peak 0.091 (calibrated: 0.55).
    mol = _render("molina", 5, tmp_path / "m")
    fai = _render("faiyaz", 5, tmp_path / "f")
    m_data, m_rate = _read(mol.mix)
    f_data, f_rate = _read(fai.mix)
    m_mono = m_data.mean(axis=1)
    f_mono = f_data.mean(axis=1)
    m_ratio = band_energy(m_mono, m_rate, 250, 4000) / band_energy(m_mono, m_rate, 40, 250)
    f_ratio = band_energy(f_mono, f_rate, 250, 4000) / band_energy(f_mono, f_rate, 40, 250)
    assert m_ratio > f_ratio * 0.5
    assert m_ratio > 0.055
    k_data, _ = _read(mol.stems[Role.KEYS])
    assert 0.3 < float(np.abs(k_data).max()) < 0.9


def test_tunisia_renders_bridge_form_end_to_end(tmp_path: Path) -> None:
    try:
        load_kit()
    except FileNotFoundError:
        pytest.skip("kit not fetched")
    beat = make_beat(style="tunisia", key="Am", bpm=88, bars=2, n=1, seed=5)[0]
    assert beat.section_b is not None
    result = render_beat(beat, tmp_path)
    assert result.master.exists()
    assert Role.KEYS in result.stems and result.stems[Role.KEYS].exists()
    k_data, _ = _read(result.stems[Role.KEYS])
    assert 0.3 < float(np.abs(k_data).max()) < 0.9
    m_data, _ = _read(result.mix)
    assert float(np.abs(m_data).max()) > 0.1
