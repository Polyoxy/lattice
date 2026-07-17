from pathlib import Path

import pytest

from lattice import make_beat
from lattice.render.engine import render_beat
from lattice.render.kits import load_kit


def test_render_beat_end_to_end(tmp_path: Path) -> None:
    try:
        load_kit()
    except FileNotFoundError:
        pytest.skip("kit not fetched")
    beat = make_beat(style="faiyaz", key="Am", bpm=90, bars=2, n=1, seed=3)[0]
    result = render_beat(beat, tmp_path)
    assert result.master.exists() and result.mix.exists()
    assert result.stems and all(p.exists() for p in result.stems.values())


def test_molina_drumless_renders_without_kit(tmp_path: Path) -> None:
    from lattice.cards import MOLINA

    beat = make_beat(
        style=MOLINA.override(p_drumless=1.0), key="Cm", bpm=80, bars=2, n=1, seed=1
    )[0]
    result = render_beat(beat, tmp_path)
    assert result.master.exists()
