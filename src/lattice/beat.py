from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass, field, replace
from importlib import metadata
from pathlib import Path

from lattice.cards import StyleCard
from lattice.groove.pocket import PocketReport
from lattice.harmony.elaborate import Segment
from lattice.harmony.grammar import Loop
from lattice.midi import programs_for_card, write_midi
from lattice.model import Event, Role, Timeline
from lattice.section import SectionRender
from lattice.theory.chord import symbol
from lattice.theory.key import Key, key_name
from lattice.theory.pitch import SpelledPitch

_SF2_DIR = Path("/usr/share/sounds/sf2")


@dataclass(frozen=True, slots=True)
class Beat:
    card: StyleCard
    key: Key
    bpm: int
    bars: int
    seed: int
    index: int = field(default=0, kw_only=True)
    loop: Loop
    segments: tuple[Segment, ...]
    voicings: tuple[tuple[SpelledPitch, ...], ...]
    parts_a: dict[Role, tuple[Event, ...]]
    parts_b: dict[Role, tuple[Event, ...]]
    timeline: Timeline
    pocket: PocketReport
    score: float
    section_b: SectionRender | None = field(default=None, kw_only=True)

    def unrolled(self) -> dict[Role, tuple[Event, ...]]:
        out: dict[Role, list[Event]] = {r: [] for r in Role}
        cycle = 0
        cycle_ticks = self.bars * 3840
        for section in self.timeline.sections:
            if self.section_b is not None:
                parts = self.section_b.parts_a if section.kind == "b" else self.parts_a
            else:
                parts = self.parts_b if section.kind == "b" else self.parts_a
            for _ in range(section.cycles):
                offset = cycle * cycle_ticks
                for role, events in parts.items():
                    if role in section.muted:
                        continue
                    for e in events:
                        moved = replace(e, tick=e.tick + offset)
                        if section.transpose and e.pitch is not None:
                            moved = replace(moved, pitch=e.pitch + section.transpose)
                        out[role].append(moved)
                cycle += 1
        return {r: tuple(sorted(v, key=lambda e: e.tick)) for r, v in out.items()}

    def to_midi(self, path: str) -> None:
        write_midi(self.unrolled(), self.bpm, path, programs=programs_for_card(self.card.name))

    def to_json(self) -> str:
        def ev(e: Event) -> dict[str, object]:
            return {
                "tick": e.tick, "dur": e.dur, "vel": e.vel, "pitch": e.pitch,
                "drum": e.drum.value if e.drum else None,
                "micro_ms": round(e.micro_ms, 4), "glide": e.glide,
            }

        def render_dict(
            loop: Loop,
            segments: tuple[Segment, ...],
            voicings: tuple[tuple[SpelledPitch, ...], ...],
            parts_a: dict[Role, tuple[Event, ...]],
            parts_b: dict[Role, tuple[Event, ...]],
        ) -> dict[str, object]:
            return {
                "loop": [fc.name for fc in loop.items],
                "segments": [
                    {
                        "symbol": symbol(s.chord),
                        "label": s.label,
                        "start": s.start_slot,
                        "dur": s.dur_slots,
                    }
                    for s in segments
                ],
                "voicings": [[p.name() for p in v] for v in voicings],
                "parts_a": {
                    r.value: [ev(e) for e in es]
                    for r, es in sorted(parts_a.items(), key=lambda kv: kv[0].value)
                },
                "parts_b": {
                    r.value: [ev(e) for e in es]
                    for r, es in sorted(parts_b.items(), key=lambda kv: kv[0].value)
                },
            }

        data = {
            "card": asdict(self.card),
            "key": key_name(self.key),
            "bpm": self.bpm,
            "engine": metadata.version("lattice"),
            "bars": self.bars,
            "seed": self.seed,
            "index": self.index,
            "score": round(self.score, 6),
            **render_dict(self.loop, self.segments, self.voicings, self.parts_a, self.parts_b),
            "section_b": (
                render_dict(
                    self.section_b.loop,
                    self.section_b.segments,
                    self.section_b.voicings,
                    self.section_b.parts_a,
                    self.section_b.parts_b,
                )
                if self.section_b is not None
                else None
            ),
            "pocket": {
                "swing": round(self.pocket.swing, 4),
                "snap_ms": round(self.pocket.snap_ms, 2),
                "clap_ms": round(self.pocket.clap_ms, 2),
            },
            "timeline": [
                {
                    "kind": s.kind, "cycles": s.cycles, "transpose": s.transpose,
                    "muted": sorted(r.value for r in s.muted),
                }
                for s in self.timeline.sections
            ],
        }
        return json.dumps(data, sort_keys=True)

    def save(self, dir_path: str) -> None:
        d = Path(dir_path)
        d.mkdir(parents=True, exist_ok=True)
        self.to_midi(str(d / "beat.mid"))
        (d / "beat.json").write_text(self.to_json())

    def preview(self, wav_path: str) -> bool:
        if shutil.which("fluidsynth") is None or not _SF2_DIR.is_dir():
            return False
        fonts = sorted(_SF2_DIR.glob("*.sf2"))
        if not fonts:
            return False
        mid = Path(wav_path).with_suffix(".mid")
        self.to_midi(str(mid))
        subprocess.run(
            ["fluidsynth", "-ni", str(fonts[0]), str(mid), "-F", wav_path, "-r", "44100"],
            check=True, capture_output=True,
        )
        return True

    def explain(self) -> str:
        from lattice.explain import explain_beat

        return explain_beat(self)
