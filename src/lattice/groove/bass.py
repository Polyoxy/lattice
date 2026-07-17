from __future__ import annotations

import numpy as np

from lattice.cards import StyleCard
from lattice.harmony.elaborate import Segment
from lattice.model import Event, Role
from lattice.theory.chord import fifth_interval
from lattice.theory.pitch import pitch_class

_SLOT = 480


def _sub_pitch(root_tpc: int) -> int:
    pc = pitch_class(root_tpc)
    return min((pc + 12 * o for o in range(0, 5)), key=lambda m: (abs(m - 31), -m))


def _nearest_low(pc: int) -> int:
    return min((pc + 12 * o for o in range(5) if 28 <= pc + 12 * o <= 52))


def _two_feel(segments: tuple[Segment, ...]) -> tuple[Event, ...]:
    events: list[Event] = []
    for seg in segments:
        seg_start = seg.start_slot * _SLOT
        seg_end = seg_start + seg.dur_slots * _SLOT
        i = 0
        t = seg_start
        while t < seg_end:
            pc_root = pitch_class(seg.chord.root)
            pc = pc_root if i % 2 == 0 else pitch_class(seg.chord.root + fifth_interval(seg.chord))
            vel = 78 if i % 2 == 0 else 72
            events.append(Event(t, min(1920, seg_end - t), vel, pitch=_nearest_low(pc)))
            i += 1
            t += 1920
    return tuple(events)


def _walk(segments: tuple[Segment, ...], rng: np.random.Generator) -> tuple[Event, ...]:
    events: list[Event] = []
    for si, seg in enumerate(segments):
        seg_start = seg.start_slot * _SLOT
        seg_end = seg_start + seg.dur_slots * _SLOT
        nxt_root = pitch_class(segments[(si + 1) % len(segments)].chord.root)
        chord_pcs = [pitch_class(t_) for t_ in (seg.chord.root, *(
            seg.chord.root + i for i in seg.chord.intervals
        ))]
        t = seg_start
        beat = 0
        while t < seg_end:
            last_beat = t + 960 >= seg_end
            if last_beat:
                target = _nearest_low(nxt_root)
                step = int(rng.choice(np.array([-1, 1, -2]), p=np.array([0.5, 0.3, 0.2])))
                pitch = int(np.clip(target + step, 28, 52))
                vel = 68
            elif beat % 2 == 0:
                idx = 0 if beat == 0 else min(2, len(chord_pcs) - 1)
                pitch = _nearest_low(chord_pcs[idx])
                vel = 76
            else:
                pitch = _nearest_low(chord_pcs[min(1, len(chord_pcs) - 1)])
                vel = 70
            events.append(Event(t, min(960, seg_end - t), vel, pitch=pitch))
            beat += 1
            t += 960
    return tuple(events)


def bass_parts(
    segments: tuple[Segment, ...], card: StyleCard, rng: np.random.Generator
) -> dict[Role, tuple[Event, ...]]:
    if card.bass_feel == "two":
        return {Role.SUB: (), Role.BASS: _two_feel(segments)}
    if card.bass_feel == "walk":
        return {Role.SUB: (), Role.BASS: _walk(segments, rng)}
    sub_pitches = [_sub_pitch(s.chord.root) for s in segments]
    sub = tuple(
        Event(s.start_slot * _SLOT, s.dur_slots * _SLOT, 92, pitch=p)
        for s, p in zip(segments, sub_pitches, strict=True)
    )
    bass: list[Event] = []
    for i, s in enumerate(segments):
        start = s.start_slot * _SLOT
        root = sub_pitches[i] + 12
        bass.append(Event(start, min(2, s.dur_slots) * _SLOT, 84, pitch=root))
        nxt = sub_pitches[(i + 1) % len(segments)]
        boundary = (s.start_slot + s.dur_slots) * _SLOT
        stab_fires = rng.random() < card.p_bass_stab and s.dur_slots >= 4
        approach_fires = rng.random() < card.p_bass_approach and s.dur_slots >= 2
        if stab_fires:
            bass.append(Event(start + 1440, 240, 72, pitch=root))
            if not (approach_fires and boundary - 240 == start + 1680):
                bass.append(Event(start + 1680, 240, 64, pitch=root))
        if approach_fires:
            glide = bool(rng.random() < card.p_bass_glide)
            bass.append(Event(boundary - 240, 240, 70, pitch=nxt + 12 - 1, glide=glide))
    return {Role.SUB: sub, Role.BASS: tuple(sorted(bass, key=lambda e: e.tick))}
