from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from lattice.beat import Beat
from lattice.model import Role
from lattice.render.kits import load_kit
from lattice.render.master import master
from lattice.render.mix import render_mix
from lattice.render.stems import render_keys_fluidsynth, render_role_stem

_DRUM_ROLES: Final[frozenset[Role]] = frozenset({Role.KICK, Role.SNARE, Role.HAT, Role.PERC})
_FLUIDSYNTH_KEYS_CARDS: Final[frozenset[str]] = frozenset({"molina", "tunisia"})


@dataclass(frozen=True, slots=True)
class RenderResult:
    stems: dict[Role, Path]
    mix: Path
    master: Path


def render_beat(beat: Beat, out_dir: str | Path) -> RenderResult:
    out = Path(out_dir)
    stems_dir = out / "stems"
    stems_dir.mkdir(parents=True, exist_ok=True)

    unrolled = beat.unrolled()
    kit = load_kit() if any(unrolled[role] for role in _DRUM_ROLES) else None

    stems: dict[Role, Path] = {}
    for role in Role:
        if not unrolled[role]:
            continue
        stem_path = stems_dir / f"{role.value}.wav"
        if role is Role.KEYS and beat.card.name in _FLUIDSYNTH_KEYS_CARDS:
            render_keys_fluidsynth(beat, stem_path)
        else:
            render_role_stem(beat, role, stem_path, kit=kit)
        stems[role] = stem_path

    mix_path = out / "mix.wav"
    render_mix(beat, stems, mix_path)

    master_path = out / "master.wav"
    master(mix_path, master_path)

    return RenderResult(stems=stems, mix=mix_path, master=master_path)
