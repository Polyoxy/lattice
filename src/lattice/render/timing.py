from __future__ import annotations

from dataclasses import dataclass

from lattice.beat import Beat
from lattice.model import DrumSound, Event, ms_per_tick


@dataclass(frozen=True, slots=True)
class Note:
    onset_s: float
    dur_s: float
    amp: float
    freq: float | None
    drum: DrumSound | None
    glide: bool


def to_notes(events: tuple[Event, ...], bpm: int) -> tuple[Note, ...]:
    mpt = ms_per_tick(bpm)
    notes = [
        Note(
            onset_s=max(0.0, e.tick * mpt + e.micro_ms) / 1000.0,
            dur_s=e.dur * mpt / 1000.0,
            amp=e.vel / 127.0,
            freq=440.0 * 2 ** ((e.pitch - 69) / 12) if e.pitch is not None else None,
            drum=e.drum,
            glide=e.glide,
        )
        for e in events
    ]
    return tuple(sorted(notes, key=lambda n: n.onset_s))


def total_seconds(beat: Beat) -> float:
    return beat.timeline.total_cycles * beat.bars * 4 * 60.0 / beat.bpm + 1.5
