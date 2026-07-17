import json
import shutil
from pathlib import Path

import mido
import numpy as np
import pytest

import lattice
from lattice import make_beat
from lattice.arrange import build_timeline
from lattice.beat import Beat
from lattice.cards import FAIYAZ
from lattice.groove.bass import bass_parts
from lattice.groove.drums import faiyaz_patterns
from lattice.groove.keys import keys_events
from lattice.groove.pocket import apply_pocket
from lattice.harmony.elaborate import elaborate
from lattice.harmony.functions import build_function
from lattice.harmony.grammar import Loop
from lattice.midi import write_midi
from lattice.model import Event, Role
from lattice.theory.key import parse_key
from lattice.voicing.realize import realize


def _beat(seed: int = 0) -> Beat:
    key = parse_key("Am")
    loop = Loop(key, (build_function(key, "i9"), build_function(key, "bVImaj7")), bars=4)
    rng = np.random.default_rng(seed)
    segments = elaborate(loop, FAIYAZ, rng)
    voicings = realize(segments, FAIYAZ)
    drums = faiyaz_patterns(FAIYAZ, 4, rng)
    other = {
        **bass_parts(segments, FAIYAZ, rng),
        Role.KEYS: keys_events(segments, voicings, 4, FAIYAZ, rng),
    }
    rng_a = np.random.default_rng(seed + 1000)
    rng_b = np.random.default_rng(seed + 1000)
    parts_a, report = apply_pocket({**drums["A"], **other}, FAIYAZ, 72, rng_a)
    parts_b, _ = apply_pocket({**drums["B"], **other}, FAIYAZ, 72, rng_b)
    timeline = build_timeline(FAIYAZ, 4, 72, np.random.default_rng(seed))
    return Beat(
        card=FAIYAZ, key=key, bpm=72, bars=4, seed=seed, loop=loop, segments=segments,
        voicings=voicings, parts_a=parts_a, parts_b=parts_b, timeline=timeline,
        pocket=report, score=0.0,
    )


def test_unrolled_respects_intro_mutes() -> None:
    b = _beat()
    events = b.unrolled()
    intro_end = b.bars * 3840
    assert all(e.tick >= intro_end for e in events[Role.KICK])
    assert any(e.tick < intro_end for e in events[Role.KEYS])


def test_midi_file_structure(tmp_path: Path) -> None:
    b = _beat()
    p = tmp_path / "beat.mid"
    b.to_midi(str(p))
    mid = mido.MidiFile(str(p))
    assert mid.ticks_per_beat == 960
    tempos = [m for t in mid.tracks for m in t if m.type == "set_tempo"]
    assert tempos and tempos[0].tempo == mido.bpm2tempo(72)
    drum_ons = [
        m for t in mid.tracks for m in t
        if m.type == "note_on" and m.channel == 9 and m.velocity > 0
    ]
    n_drums = sum(
        len(b.unrolled()[r]) for r in (Role.KICK, Role.SNARE, Role.HAT, Role.PERC)
    )
    assert len(drum_ons) == n_drums


def test_write_midi_clamps_overlapping_same_note_reattacks(tmp_path: Path) -> None:
    beat = make_beat(style="conductor", key="Cm", bpm=90, n=1, seed=3)[0]
    n_events = sum(len(events) for events in beat.unrolled().values())

    p = tmp_path / "beat.mid"
    beat.to_midi(str(p))
    mid = mido.MidiFile(str(p))

    active: set[tuple[int, int]] = set()
    n_note_on = 0
    for track in mid.tracks:
        tick = 0
        for msg in track:
            tick += msg.time
            if msg.type == "note_on":
                note_key = (msg.channel, msg.note)
                assert note_key not in active, f"note_on for {note_key} at tick {tick} while active"
                active.add(note_key)
                n_note_on += 1
            elif msg.type == "note_off":
                active.discard((msg.channel, msg.note))

    assert n_note_on == n_events


def test_json_is_deterministic_and_parseable() -> None:
    b = _beat()
    j1, j2 = b.to_json(), b.to_json()
    assert j1 == j2
    data = json.loads(j1)
    assert data["bpm"] == 72 and data["card"]["name"] == "faiyaz"


def test_save_writes_both_artifacts(tmp_path: Path) -> None:
    b = _beat()
    b.save(str(tmp_path))
    assert (tmp_path / "beat.mid").exists() and (tmp_path / "beat.json").exists()


@pytest.mark.skipif(shutil.which("fluidsynth") is None, reason="no fluidsynth")
def test_preview_renders_wav(tmp_path: Path) -> None:
    b = _beat()
    wav = tmp_path / "p.wav"
    ok = b.preview(str(wav))
    if ok:
        assert wav.exists() and wav.stat().st_size > 1000


def test_molina_preview_uses_grand_piano(tmp_path: Path) -> None:
    from lattice import make_beat

    b = make_beat(style="molina", key="Cm", bpm=80, n=1, seed=5)[0]
    p = tmp_path / "molina_prog_test.mid"
    b.to_midi(str(p))
    mid = mido.MidiFile(str(p))
    programs = {
        (m.channel, m.program)
        for t in mid.tracks
        for m in t
        if m.type == "program_change"
    }
    assert (0, 0) in programs


def test_json_records_engine_version() -> None:
    b = _beat()
    data = json.loads(b.to_json())
    assert data["engine"] == lattice.__version__


def test_write_midi_emits_cc11(tmp_path: Path) -> None:
    events = {Role.PAD: (Event(0, 1920, 60, pitch=72),)}
    path = tmp_path / "cc.mid"
    write_midi(events, 112, str(path), cc11={Role.PAD: ((0, 84), (960, 100), (1920, 116))})
    mid = mido.MidiFile(str(path))
    ccs = [m for t in mid.tracks for m in t if m.type == "control_change"]
    assert [c.value for c in ccs] == [84, 100, 116]
    assert all(c.control == 11 for c in ccs)
