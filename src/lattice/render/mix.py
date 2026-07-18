from __future__ import annotations

from pathlib import Path
from typing import Final

import supriya

from lattice.beat import Beat
from lattice.model import Role
from lattice.render.buses import (
    ballroom_bus,
    chase_bus,
    conductor_bus,
    faiyaz_bus,
    master_out,
    molina_bus,
    stem_player,
)
from lattice.render.timing import total_seconds

_CUE_FRAMES: Final = 32768
_BASS_ROLES: Final = frozenset({Role.BASS, Role.SUB})

_FAIYAZ_ROWS: Final[dict[Role, tuple[float, float, float]]] = {
    Role.KEYS: (-3.0, 0.0, 0.0),
    Role.BASS: (-4.0, 0.0, 1.0),
    Role.SUB: (-2.5, 0.0, 1.0),
    Role.KICK: (0.0, 0.0, 0.0),
    Role.SNARE: (-1.5, 0.06, 0.0),
    Role.HAT: (-7.0, -0.12, 0.0),
    Role.PERC: (-10.0, 0.18, 0.0),
}
_CONDUCTOR_ROWS: Final[dict[Role, tuple[float, float, float]]] = {
    Role.KEYS: (-2.0, 0.0, 0.0),
    Role.BASS: (-5.0, 0.0, 1.0),
    Role.SUB: (-4.0, 0.0, 1.0),
    Role.KICK: (-1.0, 0.0, 0.0),
    Role.SNARE: (-2.0, 0.04, 0.0),
    Role.HAT: (-8.0, -0.1, 0.0),
    Role.PERC: (-12.0, 0.12, 0.0),
}
_MOLINA_ROWS: Final[dict[Role, tuple[float, float, float]]] = {
    Role.KEYS: (-1.5, 0.0, 0.0),
    Role.BASS: (-4.5, 0.0, 1.0),
    Role.SUB: (-6.0, 0.0, 1.0),
    Role.KICK: (-4.0, 0.0, 0.0),
    Role.SNARE: (-5.0, 0.05, 0.0),
    Role.HAT: (-10.0, -0.08, 0.0),
    Role.PERC: (-12.0, 0.1, 0.0),
}
_BALLROOM_ROWS: Final[dict[Role, tuple[float, float, float]]] = {
    Role.KEYS: (-1.5, 0.0, 0.0),
    Role.BASS: (-5.0, 0.0, 1.0),
    Role.PAD: (-8.0, 0.0, 0.0),
    Role.KICK: (-15.0, 0.0, 0.0),
    Role.SNARE: (-14.0, 0.05, 0.0),
    Role.HAT: (-16.0, -0.08, 0.0),
}
_CHASE_ROWS: Final[dict[Role, tuple[float, float, float]]] = {
    Role.KEYS: (-2.0, 0.0, 0.0),
    Role.LEAD: (-3.0, 0.0, 0.0),
    Role.PAD: (-9.0, 0.0, 0.0),
    Role.BASS: (-6.0, 0.0, 1.0),
    Role.SUB: (-4.0, 0.0, 1.0),
    Role.KICK: (-6.0, 0.0, 0.0),
    Role.SNARE: (-10.0, 0.06, 0.0),
    Role.HAT: (-11.0, -0.1, 0.0),
}

MIX_TABLE: Final[dict[str, dict[Role, tuple[float, float, float]]]] = {
    "faiyaz": _FAIYAZ_ROWS,
    "conductor": _CONDUCTOR_ROWS,
    "molina": _MOLINA_ROWS,
    "tunisia": _MOLINA_ROWS,
    "ballroom": _BALLROOM_ROWS,
    "chase": _CHASE_ROWS,
}


@supriya.synthdef()
def _passthrough(in_bus: float = 0.0, out: float = 0.0) -> None:
    from supriya.ugens import In, Out

    Out.ar(bus=out, source=In.ar(bus=in_bus, channel_count=2))


def _cue(score: supriya.Score, path: Path) -> supriya.Buffer:
    buffer_ = score.add_buffer(channel_count=2, frame_count=_CUE_FRAMES)
    buffer_.read(file_path=path.resolve(), leave_open=True)
    return buffer_


def render_mix(beat: Beat, stem_paths: dict[Role, Path], out_path: Path) -> Path:
    card_name = beat.card.name
    rows = MIX_TABLE[card_name]
    is_faiyaz = card_name == "faiyaz"
    texture = dict(beat.card.texture)

    score = supriya.Score(output_bus_channel_count=2)
    with score.at(0):
        score.add_synthdefs(
            stem_player, faiyaz_bus, conductor_bus, molina_bus, ballroom_bus,
            chase_bus, master_out, _passthrough,
        )
        keys_bus = score.add_bus_group(calculation_rate="audio", count=2)
        bass_bus = score.add_bus_group(calculation_rate="audio", count=2)
        drums_bus = score.add_bus_group(calculation_rate="audio", count=2)
        kick_key_bus = score.add_bus_group(calculation_rate="audio", count=2)
        master_bus = score.add_bus_group(calculation_rate="audio", count=2)
        final_bus = score.add_bus_group(calculation_rate="audio", count=2)

        for role, path in stem_paths.items():
            if not path.exists():
                continue
            gain_db, pan, mono = rows[role]
            gain = 10.0 ** (gain_db / 20.0)
            if role in (Role.KEYS, Role.PAD, Role.LEAD):
                target = keys_bus
            elif role in _BASS_ROLES:
                target = bass_bus
            else:
                target = drums_bus
            main_cue = _cue(score, path)
            score.add_synth(
                stem_player,
                add_action="add_to_tail",
                buffer_id=main_cue,
                out=target,
                gain=gain,
                pan=pan,
                mono=mono,
            )
            if role is Role.KICK and is_faiyaz:
                key_cue = _cue(score, path)
                score.add_synth(
                    stem_player,
                    add_action="add_to_tail",
                    buffer_id=key_cue,
                    out=kick_key_bus,
                    gain=1.0,
                    pan=0.0,
                    mono=0.0,
                )

        score.add_synth(_passthrough, add_action="add_to_tail", in_bus=bass_bus, out=master_bus)
        score.add_synth(_passthrough, add_action="add_to_tail", in_bus=drums_bus, out=master_bus)
        if is_faiyaz:
            score.add_synth(
                faiyaz_bus,
                add_action="add_to_tail",
                in_bus=keys_bus,
                kick_bus=kick_key_bus,
                out=master_bus,
                lpf_hz=texture["lpf_hz"],
                pump_db=texture["pump_db"],
            )
        else:
            score.add_synth(
                _passthrough, add_action="add_to_tail", in_bus=keys_bus, out=master_bus
            )

        if card_name == "conductor":
            score.add_synth(
                conductor_bus,
                add_action="add_to_tail",
                in_bus=master_bus,
                out=final_bus,
                lpf_hz=texture["lpf_hz"],
                wow_depth=texture["wow_depth"],
                pump_db=texture["pump_db"],
            )
        elif card_name in ("molina", "tunisia"):
            score.add_synth(
                molina_bus,
                add_action="add_to_tail",
                in_bus=master_bus,
                out=final_bus,
                lpf_hz=texture["lpf_hz"],
            )
        elif card_name == "ballroom":
            score.add_synth(
                ballroom_bus,
                add_action="add_to_tail",
                in_bus=master_bus,
                out=final_bus,
                lpf_hz=texture["lpf_hz"],
                room_size=texture["room_size"],
                verb_mix=texture["verb_mix"],
                glue_db=texture["glue_db"],
            )
        elif card_name == "chase":
            score.add_synth(
                chase_bus,
                add_action="add_to_tail",
                in_bus=master_bus,
                out=final_bus,
                lpf_hz=texture["lpf_hz"],
                room_size=texture["room_size"],
                verb_mix=texture["verb_mix"],
                glue_db=texture["glue_db"],
            )
        else:
            score.add_synth(
                _passthrough, add_action="add_to_tail", in_bus=master_bus, out=final_bus
            )

        score.add_synth(
            master_out,
            add_action="add_to_tail",
            in_bus=final_bus,
            out=0,
            lpf_hz=texture["lpf_hz"],
        )

    output_file_path, exit_code = supriya.render(
        score,
        output_file_path=Path(out_path),
        duration=total_seconds(beat),
        sample_rate=44100,
        header_format="wav",
        sample_format="int16",
    )
    if exit_code != 0 or output_file_path is None:
        raise RuntimeError(f"scsynth NRT render failed with exit code {exit_code}")
    return out_path
