from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Final

import supriya

from lattice.beat import Beat
from lattice.model import DrumSound, Role, ms_per_tick
from lattice.render.synthdefs import bassgtr, drum, pad, rhodey, subbass
from lattice.render.timing import to_notes, total_seconds

_SF2 = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
# Anchored to the repo root (uv editable src-layout install) so renders work
# from any cwd instead of only the checkout directory.
_PIANO_DIR = Path(__file__).resolve().parents[3] / "assets" / "piano"
# fluidsynth's default master gain is 0.2, which lands the piano ~20dB under the
# scsynth stems; calibrated so probe keys stems peak inside [0.3, 0.9].
_FLUIDSYNTH_GAIN: Final = 1.2


def _piano_sf2() -> Path:
    candidates = sorted(_PIANO_DIR.glob("*.sf2"))
    if not candidates:
        print(
            f"no piano soundfont in {_PIANO_DIR}, falling back to GM: {_SF2}",
            file=sys.stderr,
        )
        return _SF2
    return candidates[0]

ROLE_AMP: Final[dict[Role, float]] = {
    Role.KEYS: 0.55,
    Role.BASS: 0.5,
    Role.SUB: 0.6,
    Role.KICK: 0.9,
    Role.SNARE: 0.85,
    Role.HAT: 0.5,
    Role.PERC: 0.4,
}
_PITCHED: Final[dict[Role, supriya.SynthDef]] = {
    Role.KEYS: rhodey,
    Role.BASS: bassgtr,
    Role.SUB: subbass,
}
_DRUM_ROLES: Final[frozenset[Role]] = frozenset({Role.KICK, Role.SNARE, Role.HAT, Role.PERC})


def render_role_stem(
    beat: Beat, role: Role, out_path: Path, kit: dict[DrumSound, Path] | None
) -> Path:
    events = beat.unrolled()[role]
    if not events:
        return out_path
    notes = to_notes(events, beat.bpm)
    score = supriya.Score(output_bus_channel_count=2)
    buffers: dict[DrumSound, supriya.Buffer] = {}
    with score.at(0):
        score.add_synthdefs(rhodey, pad, subbass, bassgtr, drum)
        if role in _DRUM_ROLES:
            assert kit is not None
            for sound in {n.drum for n in notes if n.drum is not None}:
                buffers[sound] = score.add_buffer(file_path=kit[sound].resolve())
    for note in notes:
        if role in _DRUM_ROLES:
            assert note.drum is not None
            rate = 0.9 if note.drum is DrumSound.GHOST_KICK else 1.0
            with score.at(note.onset_s):
                score.add_synth(
                    drum,
                    buffer_id=buffers[note.drum],
                    amplitude=note.amp * ROLE_AMP[role],
                    rate=rate,
                )
        else:
            assert note.freq is not None
            with score.at(note.onset_s):
                synth = score.add_synth(
                    _PITCHED[role],
                    frequency=note.freq,
                    amplitude=note.amp * ROLE_AMP[role],
                    glide=1.0 if note.glide else 0.0,
                )
            with score.at(note.onset_s + note.dur_s):
                synth.set(gate=0)
    output_file_path, exit_code = supriya.render(
        score,
        output_file_path=out_path,
        duration=total_seconds(beat),
        sample_rate=44100,
        header_format="wav",
        sample_format="int24",
    )
    if exit_code != 0 or output_file_path is None:
        raise RuntimeError(f"scsynth NRT render failed with exit code {exit_code}")
    return out_path


_FLUID_VOICES: Final[dict[str, dict[Role, str]]] = {
    "molina": {Role.KEYS: "piano"},
    "tunisia": {Role.KEYS: "piano"},
    "ballroom": {Role.KEYS: "piano", Role.BASS: "gm", Role.PAD: "gm"},
    "chase": {Role.KEYS: "piano", Role.LEAD: "gm", Role.PAD: "gm"},
}
_SWELL_STEPS: Final = 8
_SWELL_MIN_DUR: Final = 960


def fluid_roles(card_name: str) -> dict[Role, str]:
    return _FLUID_VOICES.get(card_name, {})


def _swell_ramps(beat: Beat, role: Role) -> tuple[tuple[int, int], ...]:
    # Anchor each ramp to the same humanized note_on tick write_midi computes,
    # or micro-timed pads sound before their swell-start CC and inherit the
    # previous chord's full-swell tail. The dur filter exempts short stabs
    # from swells for any role: ballroom's sustained pads all pass, while
    # chase's PAD answer stabs and short LEAD notes are excluded by design.
    mpt = ms_per_tick(beat.bpm)
    ramps: list[tuple[int, int]] = []
    for e in beat.unrolled()[role]:
        if e.dur < _SWELL_MIN_DUR:
            continue
        start = max(0, e.tick + round(e.micro_ms / mpt))
        for k in range(_SWELL_STEPS):
            tick = start + (e.dur * k) // _SWELL_STEPS
            value = 84 + (32 * k) // (_SWELL_STEPS - 1)
            ramps.append((tick, value))
    return tuple(sorted(set(ramps)))


def _write_fluid_midi(beat: Beat, role: Role, mid: Path) -> None:
    from lattice.midi import programs_for_card, write_midi

    cc: dict[Role, tuple[tuple[int, int], ...]] | None = (
        {role: _swell_ramps(beat, role)} if role in (Role.PAD, Role.LEAD) else None
    )
    write_midi(
        beat.unrolled(), beat.bpm, str(mid),
        programs=programs_for_card(beat.card.name), roles={role}, cc11=cc,
    )


def render_fluid_stem(beat: Beat, role: Role, out_path: Path) -> Path:
    sf2 = _piano_sf2() if _FLUID_VOICES[beat.card.name][role] == "piano" else _SF2
    mid = out_path.with_suffix(".mid")
    _write_fluid_midi(beat, role, mid)
    subprocess.run(
        [
            "fluidsynth", "-ni", "-g", str(_FLUIDSYNTH_GAIN),
            "-F", str(out_path), "-r", "44100", str(sf2), str(mid),
        ],
        check=True, capture_output=True,
    )
    mid.unlink()
    return out_path
