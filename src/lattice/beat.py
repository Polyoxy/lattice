from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

from lattice.cards import StyleCard
from lattice.groove.pocket import PocketReport
from lattice.harmony.elaborate import Segment
from lattice.harmony.grammar import Loop
from lattice.midi import write_midi
from lattice.model import Event, Role, Timeline
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

    def unrolled(self) -> dict[Role, tuple[Event, ...]]:
        out: dict[Role, list[Event]] = {r: [] for r in Role}
        cycle = 0
        cycle_ticks = self.bars * 3840
        for section in self.timeline.sections:
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
        write_midi(self.unrolled(), self.bpm, path)

    def to_json(self) -> str:
        def ev(e: Event) -> dict[str, object]:
            return {
                "tick": e.tick, "dur": e.dur, "vel": e.vel, "pitch": e.pitch,
                "drum": e.drum.value if e.drum else None,
                "micro_ms": round(e.micro_ms, 4), "glide": e.glide,
            }

        data = {
            "card": asdict(self.card),
            "key": key_name(self.key),
            "bpm": self.bpm,
            "bars": self.bars,
            "seed": self.seed,
            "index": self.index,
            "score": round(self.score, 6),
            "loop": [fc.name for fc in self.loop.items],
            "segments": [
                {
                    "symbol": symbol(s.chord),
                    "label": s.label,
                    "start": s.start_slot,
                    "dur": s.dur_slots,
                }
                for s in self.segments
            ],
            "voicings": [[p.name() for p in v] for v in self.voicings],
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
            "parts_a": {r.value: [ev(e) for e in es] for r, es in self.parts_a.items()},
            "parts_b": {r.value: [ev(e) for e in es] for r, es in self.parts_b.items()},
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
