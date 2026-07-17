import hashlib
import shutil
import time
from pathlib import Path

import pytest

from lattice import make_beat
from lattice.render.engine import render_beat
from lattice.render.kits import load_kit
from lattice.render.stems import render_keys_fluidsynth

pytestmark = pytest.mark.slow


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_render_is_deterministic(tmp_path: Path) -> None:
    try:
        load_kit()
    except FileNotFoundError:
        pytest.skip("kit not fetched")
    beat = make_beat(style="conductor", key="Cm", bpm=90, bars=2, n=1, seed=11)[0]
    a = render_beat(beat, tmp_path / "a")
    b = render_beat(beat, tmp_path / "b")
    assert _sha(a.mix) == _sha(b.mix)
    assert _sha(a.master) == _sha(b.master)


def test_two_minute_track_renders_in_budget(tmp_path: Path) -> None:
    try:
        load_kit()
    except FileNotFoundError:
        pytest.skip("kit not fetched")
    beat = make_beat(style="faiyaz", key="C#m", bpm=72, bars=4, n=1, seed=42)[0]
    t0 = time.monotonic()
    render_beat(beat, tmp_path)
    assert time.monotonic() - t0 < 480


def test_fluidsynth_keys_deterministic(tmp_path: Path) -> None:
    if shutil.which("fluidsynth") is None:
        pytest.skip("no fluidsynth")
    beat = make_beat(style="molina", key="Cm", bpm=84, bars=2, n=1, seed=7)[0]
    a = render_keys_fluidsynth(beat, tmp_path / "a.wav")
    b = render_keys_fluidsynth(beat, tmp_path / "b.wav")
    assert _sha(a) == _sha(b)
