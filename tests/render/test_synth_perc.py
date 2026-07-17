import wave
from pathlib import Path

from lattice.render.synth_perc import write_missing


def test_write_missing_produces_readable_mono_wavs(tmp_path: Path) -> None:
    written = write_missing(tmp_path)
    assert sorted(written) == [
        "bongo", "brush_swirl", "brush_tap", "chick", "feather", "ride", "shaker",
    ]
    for name in ("ride", "bongo", "shaker"):
        with wave.open(str(tmp_path / f"{name}.wav")) as w:
            assert w.getframerate() == 44100
            assert w.getnchannels() == 1
            assert w.getsampwidth() == 2
            assert w.getnframes() > 0


def test_write_missing_is_idempotent(tmp_path: Path) -> None:
    write_missing(tmp_path)
    assert write_missing(tmp_path) == []


def test_write_missing_is_deterministic(tmp_path: Path) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    write_missing(a)
    write_missing(b)
    for name in ("ride", "bongo", "shaker"):
        assert (a / f"{name}.wav").read_bytes() == (b / f"{name}.wav").read_bytes()


def test_brush_voices_generated(tmp_path: Path) -> None:
    written = write_missing(tmp_path)
    for name in ("brush_tap", "brush_swirl", "feather", "chick"):
        assert name in written
        with wave.open(str(tmp_path / f"{name}.wav")) as w:
            assert w.getframerate() == 44100
            assert w.getnchannels() == 1
            assert w.getsampwidth() == 2
            assert w.getnframes() > 0
