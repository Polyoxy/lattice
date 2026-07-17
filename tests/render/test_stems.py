import wave
from pathlib import Path

import numpy as np
import pytest

from lattice import make_beat
from lattice.model import Role
from lattice.render.stems import render_role_stem
from lattice.render.timing import total_seconds


def _tiny_beat():  # type: ignore[no-untyped-def]
    return make_beat(style="faiyaz", key="Am", bpm=90, bars=2, n=1, seed=3)[0]


def _rms(path: Path) -> float:
    with wave.open(str(path)) as w:
        raw = w.readframes(w.getnframes())
        sampwidth = w.getsampwidth()
    if sampwidth == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        ints = (
            b[:, 0].astype(np.int32)
            | (b[:, 1].astype(np.int32) << 8)
            | (b[:, 2].astype(np.int32) << 16)
        )
        ints = np.where(ints >= 2**23, ints - 2**24, ints)
        samples = ints.astype(np.float64) / float(2**23)
    else:
        samples = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    return float(np.sqrt(np.mean(samples**2))) if samples.size else 0.0


def test_keys_stem_renders_correct_duration(tmp_path: Path) -> None:
    beat = _tiny_beat()
    out = render_role_stem(beat, Role.KEYS, tmp_path / "keys.wav", kit=None)
    assert out.exists()
    with wave.open(str(out)) as w:
        seconds = w.getnframes() / w.getframerate()
    assert abs(seconds - total_seconds(beat)) < 0.2


def test_drum_stem_uses_kit(tmp_path: Path) -> None:
    import pytest

    from lattice.render.kits import load_kit

    try:
        kit = load_kit()
    except FileNotFoundError:
        pytest.skip("kit not fetched")
    beat = _tiny_beat()
    out = render_role_stem(beat, Role.KICK, tmp_path / "kick.wav", kit=kit)
    assert out.exists() and out.stat().st_size > 1000


def test_drum_stem_is_not_silent(tmp_path: Path) -> None:
    from lattice.render.kits import load_kit

    try:
        kit = load_kit()
    except FileNotFoundError:
        pytest.skip("kit not fetched")
    beat = _tiny_beat()
    out = render_role_stem(beat, Role.KICK, tmp_path / "kick.wav", kit=kit)
    assert _rms(out) > 0.0


def test_write_midi_role_filter(tmp_path: Path) -> None:
    import mido

    from lattice.midi import programs_for_card, write_midi

    beat = _tiny_beat()
    p = tmp_path / "keys_only.mid"
    write_midi(
        beat.unrolled(), beat.bpm, str(p),
        programs=programs_for_card(beat.card.name), roles={Role.KEYS},
    )
    mid = mido.MidiFile(str(p))
    channels = {m.channel for t in mid.tracks for m in t if m.type == "note_on"}
    assert channels == {0}


def test_molina_keys_render_via_fluidsynth(tmp_path: Path) -> None:
    import shutil

    import pytest

    if shutil.which("fluidsynth") is None:
        pytest.skip("no fluidsynth")
    from lattice import make_beat
    from lattice.render.stems import render_fluid_stem

    beat = make_beat(style="molina", key="Cm", bpm=84, bars=2, n=1, seed=7)[0]
    out = render_fluid_stem(beat, Role.KEYS, tmp_path / "keys.wav")
    assert out.exists() and out.stat().st_size > 100_000


def test_piano_sf2_falls_back_to_fluidr3_without_assets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from lattice.render import stems
    from lattice.render.stems import _SF2, _piano_sf2

    monkeypatch.setattr(stems, "_PIANO_DIR", tmp_path / "assets" / "piano")
    assert _piano_sf2() == _SF2
    assert "falling back" in capsys.readouterr().err


def test_piano_sf2_picks_first_sorted_asset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from lattice.render import stems
    from lattice.render.stems import _piano_sf2

    piano_dir = tmp_path / "assets" / "piano"
    piano_dir.mkdir(parents=True)
    (piano_dir / "z.sf2").write_bytes(b"RIFF")
    (piano_dir / "a.sf2").write_bytes(b"RIFF")
    monkeypatch.setattr(stems, "_PIANO_DIR", piano_dir)
    assert _piano_sf2() == piano_dir / "a.sf2"


def test_fluid_stem_midi_matches_legacy_for_molina(tmp_path: Path) -> None:
    from lattice.midi import programs_for_card, write_midi
    from lattice.render.stems import _write_fluid_midi

    beat = make_beat(style="molina", key="Ab", bpm=66, bars=2, n=1, seed=9)[0]
    legacy = tmp_path / "legacy.mid"
    write_midi(
        beat.unrolled(), beat.bpm, str(legacy),
        programs=programs_for_card("molina"), roles={Role.KEYS},
    )
    new = tmp_path / "new.mid"
    _write_fluid_midi(beat, Role.KEYS, new)
    assert legacy.read_bytes() == new.read_bytes()


def test_pad_swells_anchor_to_humanized_note_starts(tmp_path: Path) -> None:
    import mido

    from lattice.render.stems import _write_fluid_midi

    beat = make_beat(style="ballroom", key="F", bpm=112, bars=2, n=1, seed=5)[0]
    path = tmp_path / "pad.mid"
    _write_fluid_midi(beat, Role.PAD, path)
    mid = mido.MidiFile(str(path))
    for track in mid.tracks:
        tick = 0
        last_cc: int | None = None
        for msg in track:
            tick += msg.time
            if msg.type == "control_change" and msg.channel == 3 and msg.control == 11:
                last_cc = msg.value
            elif msg.type == "note_on" and msg.channel == 3:
                assert last_cc is not None and last_cc <= 92, (
                    f"note_on at tick {tick} preceded by CC11={last_cc}"
                )


def test_piano_dir_is_anchored_to_repo_root() -> None:
    from lattice.render.kits import _KIT_DIR
    from lattice.render.stems import _PIANO_DIR

    assert _PIANO_DIR.is_absolute()
    assert _KIT_DIR.is_absolute()
    assert _PIANO_DIR.parent == _KIT_DIR.parent
