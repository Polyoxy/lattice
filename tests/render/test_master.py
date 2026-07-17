import wave
from pathlib import Path

import numpy as np

from lattice.render.master import master


def _write_tone(path: Path) -> None:
    rate = 44100
    t = np.arange(int(rate * 0.5)) / rate
    tone = (np.sin(2 * np.pi * 440.0 * t) * 0.5 * 32767).astype("<i2")
    stereo = np.repeat(tone[:, None], 2, axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(stereo.tobytes())


def test_master_leaves_no_staged_siblings(tmp_path: Path) -> None:
    mix_path = tmp_path / "mix.wav"
    _write_tone(mix_path)
    out_path = tmp_path / "master.wav"
    master(mix_path, out_path)
    assert out_path.exists()
    assert list(tmp_path.glob("master_*.wav")) == []
