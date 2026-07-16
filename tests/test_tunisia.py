from pathlib import Path

import mido

from lattice import make_beat
from lattice.cards import TUNISIA, get_card


def test_tunisia_registered_with_bridge() -> None:
    assert get_card("tunisia") is TUNISIA
    assert TUNISIA.has_bridge
    assert "bII" in TUNISIA.function_pool
    assert TUNISIA.bridge_function_pool


def test_tunisia_produces_two_part_beats() -> None:
    beat = make_beat(style="tunisia", key="Dm", bpm=140, bars=4, n=1, seed=3)[0]
    assert beat.section_b is not None
    assert beat.section_b.loop.names() != beat.loop.names()


def test_tunisia_spanish_tinge_appears_across_seeds() -> None:
    hits = 0
    for seed in range(20):
        beat = make_beat(style="tunisia", key="Dm", bars=4, n=1, seed=seed)[0]
        names = beat.loop.names()
        if "bII" in names:
            hits += 1
    assert hits >= 8


def test_tunisia_bridges_contrast() -> None:
    from lattice.harmony.score import _root_motion_signature

    differ = 0
    for seed in range(20):
        beat = make_beat(style="tunisia", key="Dm", bars=4, n=1, seed=seed)[0]
        assert beat.section_b is not None
        if _root_motion_signature(beat.loop) != _root_motion_signature(beat.section_b.loop):
            differ += 1
    assert differ >= 18


def test_tunisia_preview_uses_grand_piano(tmp_path: Path) -> None:
    beat = make_beat(style="tunisia", key="Dm", bpm=140, bars=2, n=1, seed=1)[0]
    p = Path(tmp_path) / "t.mid"
    beat.to_midi(str(p))
    mid = mido.MidiFile(str(p))
    progs = {(m.channel, m.program) for t in mid.tracks for m in t if m.type == "program_change"}
    assert (0, 0) in progs
