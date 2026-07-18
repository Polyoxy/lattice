from __future__ import annotations

import math
from dataclasses import replace
from typing import Final

import numpy as np

from lattice.cards import StyleCard
from lattice.harmony.elaborate import Segment
from lattice.model import Event, Role
from lattice.theory.chord import Chord, chord_tpcs
from lattice.theory.pitch import SpelledPitch, pitch_class
from lattice.voicing.constraints import violates_min9

_SLOT: Final = 480
_BEAT: Final = 960
_LAST_DUR: Final = 960
_AVOID_MIN_DUR: Final = 960
_VEL_LO: Final = 72
_VEL_HI: Final = 96
_ANSWER_OFFSET: Final = 2 * _BEAT  # beats 3-4 of the span's first bar
_TRANSFORMS: Final[tuple[str, ...]] = ("displace", "truncate", "bend", "mock", "deny")
_REGISTERS: Final[dict[Role, tuple[int, int]]] = {
    Role.LEAD: (67, 91),
    Role.PAD: (55, 86),
    Role.KEYS: (60, 76),
}


def _round_half_down(x: float) -> int:
    """Nearest int; an exact .5 tie goes down (the engine's "heartbreak falls" rule)."""
    return math.ceil(x - 0.5)


def _place_nearest(prev: int, pc: int) -> int:
    """Nearest MIDI note with pitch class `pc` to `prev`; ties resolve downward."""
    return pc + 12 * _round_half_down((prev - pc) / 12)


def _spelled(tpc: int, midi: int) -> SpelledPitch:
    """SpelledPitch for `tpc` whose .midi equals `midi` (pitch classes must already match)."""
    zero = SpelledPitch(tpc, -1).midi
    return SpelledPitch(tpc, -1 + (midi - zero) // 12)


def _avoid_violated(tpc: int, midi: int, chord: Chord) -> bool:
    # Chord tones are re-spelled nearest to the candidate so violates_min9's absolute-midi
    # comparison catches a half-step clash on either side, not just within one fixed octave.
    # Over-flags chord tones on qualities with half-step-adjacent tones (m9/maj7 families);
    # _resolve_avoid self-corrects to a no-op (nearest tone = the candidate itself) — a
    # latent looseness if this pair is ever reused for chromatic motifs.
    tones = chord_tpcs(chord)
    stack = tuple(_spelled(t, _place_nearest(midi, pitch_class(t))) for t in tones)
    return violates_min9((*stack, _spelled(tpc, midi)), chord)


def _resolve_avoid(tpc: int, midi: int, chord: Chord) -> tuple[int, int]:
    if not _avoid_violated(tpc, midi, chord):
        return tpc, midi
    placements = [(t, _place_nearest(midi, pitch_class(t))) for t in chord_tpcs(chord)]
    return min(placements, key=lambda tm: (abs(tm[1] - midi), tm[1]))


def state_motif(
    motif: tuple[tuple[int, ...], tuple[int, ...]],
    segment: Segment,
    register: tuple[int, int],
    window_tick: int,
) -> tuple[Event, ...]:
    intervals, rhythm = motif
    n = len(intervals)
    tpcs = [segment.chord.root + iv for iv in intervals]
    ticks = [window_tick + slot * _SLOT for slot in rhythm]
    prev = _round_half_down((register[0] + register[1]) / 2)
    events = []
    for i, tpc in enumerate(tpcs):
        prev = _place_nearest(prev, pitch_class(tpc))
        midi = prev
        dur = ticks[i + 1] - ticks[i] if i + 1 < n else _LAST_DUR
        vel = _VEL_LO if n == 1 else round(_VEL_LO + (_VEL_HI - _VEL_LO) * i / (n - 1))
        if dur >= _AVOID_MIN_DUR:
            tpc, midi = _resolve_avoid(tpc, midi, segment.chord)
        events.append(Event(ticks[i], dur, vel, pitch=midi))
    return tuple(events)


def _bend(call: tuple[Event, ...], segment: Segment) -> tuple[Event, ...]:
    if not call:
        return call
    last = call[-1]
    if last.pitch is None:
        return call
    # No scale object exists here; "a scale step" is approximated as 2 semitones when that
    # lands on a real chord tone (the diatonic case), else 1 (a deterministic fallback).
    tones = {pitch_class(t) for t in chord_tpcs(segment.chord)}
    lowered = last.pitch - 2
    pitch = lowered if lowered % 12 in tones else last.pitch - 1
    return (*call[:-1], replace(last, pitch=pitch))


def _mock(call: tuple[Event, ...], segment: Segment) -> tuple[Event, ...]:
    if not call:
        return call
    result: list[Event] = []
    prev = call[0].pitch if call[0].pitch is not None else 0
    for e in call:
        if e.pitch is None:
            result.append(e)
            continue
        prev = _place_nearest(prev, (e.pitch + 2) % 12)
        result.append(replace(e, pitch=prev))
    return tuple(result)


def _deny(call: tuple[Event, ...], segment: Segment) -> tuple[Event, ...]:
    if not call:
        return call
    last = call[-1]
    if last.pitch is None:
        return call
    root = _place_nearest(last.pitch, pitch_class(segment.chord.root))
    return (*call[:-1], replace(last, pitch=root + 2))


def answer_motif(call: tuple[Event, ...], transform: str, segment: Segment) -> tuple[Event, ...]:
    if transform == "displace":
        return tuple(replace(e, tick=e.tick + _SLOT) for e in call)
    if transform == "truncate":
        return call[:-1] if len(call) > 2 else call
    if transform == "bend":
        return _bend(call, segment)
    if transform == "mock":
        return _mock(call, segment)
    if transform == "deny":
        return _deny(call, segment)
    raise ValueError(f"unknown transform: {transform!r}")


def _register_shift(events: tuple[Event, ...], lo: int, hi: int) -> tuple[Event, ...]:
    pitches = [e.pitch for e in events if e.pitch is not None]
    if not pitches:
        return events
    target = _round_half_down((lo + hi) / 2)
    current = (min(pitches) + max(pitches)) // 2
    shift = _round_half_down((target - current) / 12) * 12
    if shift == 0:
        return events
    return tuple(replace(e, pitch=e.pitch + shift) if e.pitch is not None else e for e in events)


def _fit_span(events: tuple[Event, ...], span_end: int) -> tuple[Event, ...]:
    # "Every bar" density (density_bars=1) leaves only one bar for a full call AND its
    # answer; a slot-3-final motif's forced dur=960 tail plus a displaced answer can run
    # past the span's own end. Clip a note that runs over; drop one that starts past the
    # boundary outright (mirrors truncate's own "drop rather than mis-fit" precedent) —
    # this never fires for density_bars=2 (empirically swept, 0 activations).
    fitted = []
    for e in events:
        if e.tick >= span_end:
            continue
        fitted.append(replace(e, dur=min(e.dur, span_end - e.tick)))
    return tuple(fitted)


def _segment_at(segments: tuple[Segment, ...], tick: int) -> Segment:
    slot = tick // _SLOT
    for seg in segments:
        if seg.start_slot <= slot < seg.start_slot + seg.dur_slots:
            return seg
    return segments[-1]


def conversation(
    segments: tuple[Segment, ...],
    card: StyleCard,
    bars: int,
    rng: np.random.Generator,
    *,
    caller: Role,
    answerers: tuple[Role, ...],
    density_bars: int,
    answers_only: bool = False,
) -> dict[Role, tuple[Event, ...]]:
    span_ticks = density_bars * 8 * _SLOT
    calls: list[Event] = []
    answers: dict[Role, list[Event]] = {r: [] for r in answerers}
    for span_i in range(bars // density_bars):
        span_start = span_i * span_ticks
        span_end = span_start + span_ticks
        motif = card.motifs[int(rng.integers(len(card.motifs)))]
        transform = _TRANSFORMS[int(rng.integers(len(_TRANSFORMS)))]
        # Fixed draw order (motif, transform, answerer): this slot is always consumed so
        # the draw count/sequence never depends on outcomes. Selection itself is round-robin.
        rng.integers(len(answerers))
        answerer = answerers[span_i % len(answerers)]

        call_events = state_motif(
            motif, _segment_at(segments, span_start), _REGISTERS[caller], span_start
        )
        calls.extend(_fit_span(call_events, span_end))
        # Nominal beats-3-4 start, pushed later if the call's own last note (forced to
        # dur=960 regardless of its nominal slot) rings past that mark — three of the five
        # card motifs do, since their last slot is 3 (tick 1440 + dur 960 = 2400 > 1920).
        # Without this, the answer's base window can start underneath the call's own tail.
        call_end = max((e.tick + e.dur for e in call_events), default=0)
        offset = max(_ANSWER_OFFSET, call_end - span_start)
        based = tuple(replace(e, tick=e.tick + offset) for e in call_events)
        twisted = answer_motif(based, transform, _segment_at(segments, span_start + offset))
        shifted = _register_shift(twisted, *_REGISTERS[answerer])
        answers[answerer].extend(_fit_span(shifted, span_end))

    result: dict[Role, tuple[Event, ...]] = {} if answers_only else {caller: tuple(calls)}
    for r in answerers:
        result[r] = tuple(answers[r])
    return result
