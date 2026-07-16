from __future__ import annotations

from typing import Final

import mido

from lattice.model import DrumSound, Event, Role, ms_per_tick

DRUM_NOTE: Final[dict[DrumSound, int]] = {
    DrumSound.KICK: 36, DrumSound.SNARE: 38, DrumSound.RIM: 37, DrumSound.CLAP: 39,
    DrumSound.HAT_CLOSED: 42, DrumSound.HAT_OPEN: 46, DrumSound.RIDE: 51,
    DrumSound.TOM_LO: 45, DrumSound.TOM_HI: 50, DrumSound.BONGO: 60,
    DrumSound.SHAKER: 70, DrumSound.GHOST_KICK: 36,
}
_CHANNEL: Final[dict[Role, int]] = {
    Role.KEYS: 0, Role.BASS: 1, Role.SUB: 2,
    Role.KICK: 9, Role.SNARE: 9, Role.HAT: 9, Role.PERC: 9,
}
_PROGRAM: Final[dict[Role, int]] = {Role.KEYS: 4, Role.BASS: 33, Role.SUB: 38}


def _note(e: Event) -> int:
    if e.drum is not None:
        return DRUM_NOTE[e.drum]
    assert e.pitch is not None
    return e.pitch


def write_midi(unrolled: dict[Role, tuple[Event, ...]], bpm: int, path: str) -> None:
    mid = mido.MidiFile(ticks_per_beat=960)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    meta.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
    mid.tracks.append(meta)
    mpt = ms_per_tick(bpm)
    for role, events in unrolled.items():
        if not events:
            continue
        track = mido.MidiTrack()
        ch = _CHANNEL[role]
        if role in _PROGRAM:
            track.append(mido.Message("program_change", channel=ch, program=_PROGRAM[role], time=0))
        spans: list[tuple[int, int, int, int]] = []
        for e in events:
            start = max(0, e.tick + round(e.micro_ms / mpt))
            note = _note(e)
            spans.append((start, note, e.vel, start + e.dur))
        spans.sort(key=lambda s: s[0])
        pending: dict[tuple[int, int], int] = {}
        for j, (start_j, note_j, _, _) in enumerate(spans):
            note_key = (ch, note_j)
            if note_key in pending:
                i = pending[note_key]
                start_i, note_i, vel_i, end_i = spans[i]
                spans[i] = (start_i, note_i, vel_i, min(end_i, start_j))
            pending[note_key] = j
        moments: list[tuple[int, int, mido.Message]] = []
        for start, note, vel, end in spans:
            on = mido.Message("note_on", channel=ch, note=note, velocity=vel, time=0)
            off = mido.Message("note_off", channel=ch, note=note, velocity=0, time=0)
            moments.append((start, 1, on))
            moments.append((end, 0, off))
        moments.sort(key=lambda m: (m[0], m[1]))
        prev = 0
        for tick, _, msg in moments:
            track.append(msg.copy(time=tick - prev))
            prev = tick
        mid.tracks.append(track)
    mid.save(path)
