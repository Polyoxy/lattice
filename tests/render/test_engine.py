from pathlib import Path

import pytest

from lattice import make_beat
from lattice.model import Role
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


def test_ballroom_beat_structure() -> None:
    beat = make_beat(style="ballroom", key="F", bpm=112, bars=2, n=1, seed=5)[0]
    assert beat.section_b is not None
    body = [s.kind for s in beat.timeline.sections if s.kind in ("a", "b")]
    pattern = ("a", "a", "b", "a")
    assert all(k == pattern[i % 4] for i, k in enumerate(body))
    unrolled = beat.unrolled()
    assert unrolled[Role.PAD]
    assert unrolled[Role.BASS]
    assert not unrolled[Role.SUB]


def test_chase_escalation_structure() -> None:
    beat = make_beat(style="chase", key="Dm", bpm=160, bars=2, n=1, seed=5)[0]
    assert beat.section_b is not None
    unrolled = beat.unrolled()
    assert unrolled[Role.LEAD]
    assert unrolled[Role.PAD]
    lead_ticks = {e.tick for e in unrolled[Role.LEAD]}
    body = [s.kind for s in beat.timeline.sections if s.kind in ("a", "b")]
    assert body[:3] == ["a", "a", "b"]
    # lead_enters_section=3: no LEAD event before the first "b" body section's
    # start tick (cycles accumulate across every section, intro/drop included,
    # same as Beat.unrolled()'s own offset arithmetic).
    cycles_before_b = 0
    for s in beat.timeline.sections:
        if s.kind == "b":
            break
        cycles_before_b += s.cycles
    boundary = cycles_before_b * beat.bars * 3840
    assert min(lead_ticks) >= boundary
