import wave
from pathlib import Path

from lattice.render.spike import render_sine


def test_nrt_renders_one_second_sine(tmp_path: Path) -> None:
    out = tmp_path / "sine.wav"
    render_sine(str(out), seconds=1.0, frequency=440.0)
    assert out.exists()
    with wave.open(str(out)) as w:
        assert w.getframerate() == 44100
        frames = w.getnframes()
    assert abs(frames / 44100 - 1.0) < 0.05
