from __future__ import annotations

from lattice.cards import StyleCard
from lattice.theory import interval as iv
from lattice.theory.chord import Chord, is_dominant
from lattice.theory.pitch import SpelledPitch, Tpc
from lattice.voicing.constraints import valid

_COLOR_ORDER = (
    iv.M3,
    iv.m3,
    iv.m7,
    iv.M7,
    iv.M6,
    iv.M9,
    iv.P5,
    iv.m2,
    iv.m6,
    iv.P4,
    iv.A5,
    iv.d5,
    iv.d7,
)


def _tones(chord: Chord, rootless: bool) -> list[Tpc]:
    ordered = [
        chord.root + i
        for i in _COLOR_ORDER
        if i in chord.intervals and not (i == iv.P5 and iv.m6 in chord.intervals)
    ]
    return ordered if rootless else [chord.root, *ordered]


def _rotations(tones: list[Tpc]) -> list[list[Tpc]]:
    return [tones[r:] + tones[:r] for r in range(len(tones))]


def _stack_close(
    tones: list[Tpc], bottom_octave: int, first_gap_min: int = 0
) -> tuple[SpelledPitch, ...]:
    out = [SpelledPitch(tones[0], bottom_octave)]
    for i, t in enumerate(tones[1:]):
        prev = out[-1].midi
        octave = bottom_octave - 2
        p = SpelledPitch(t, octave)
        floor = prev + (first_gap_min if i == 0 else 1)
        while p.midi < floor:
            octave += 1
            p = SpelledPitch(t, octave)
        out.append(p)
    return tuple(out)


def _drop2(close: tuple[SpelledPitch, ...]) -> tuple[SpelledPitch, ...]:
    if len(close) < 4:
        return close
    ordered = sorted(close, key=lambda p: p.midi)
    dropped = ordered[-2]
    return tuple(
        sorted(
            [
                *(p for p in ordered if p is not dropped),
                SpelledPitch(dropped.tpc, dropped.octave - 1),
            ],
            key=lambda p: p.midi,
        )
    )


def _us_triad(chord: Chord, bottom_octave: int) -> tuple[SpelledPitch, ...]:
    lower = _stack_close([chord.root + iv.M3, chord.root + iv.m7], bottom_octave)
    us_root = chord.root - 4
    upper = _stack_close([us_root, us_root + iv.M3, us_root + iv.P5], bottom_octave + 1)
    merged = [*lower, *(p for p in upper if p.midi > lower[-1].midi)]
    return tuple(sorted(merged, key=lambda p: p.midi))


def stack_candidates(
    chord: Chord, card: StyleCard, bass_covers_root: bool
) -> list[tuple[SpelledPitch, ...]]:
    rootless = card.rootless and bass_covers_root
    tones = _tones(chord, rootless)
    center = (card.register_lo + card.register_hi) / 2
    raw: list[tuple[SpelledPitch, ...]] = []
    for octave in range(2, 7):
        if "close4" in card.templates and len(tones) >= 4:
            for rot in _rotations(tones[:4]):
                raw.append(_stack_close(rot, octave))
        if "close5" in card.templates and len(tones) >= 5:
            for rot in _rotations(tones[:5]):
                raw.append(_stack_close(rot, octave))
        if "close4" in card.templates and len(tones) == 3:
            for rot in _rotations(tones):
                raw.append(_stack_close(rot, octave))
        if "spread" in card.templates and len(tones) >= 4:
            raw.append(_stack_close(tones[:4], octave, first_gap_min=12))
        if "drop2" in card.templates and len(tones) >= 4:
            raw.append(_drop2(_stack_close(tones[:4], octave)))
        if "us_triad" in card.templates and is_dominant(chord):
            raw.append(_us_triad(chord, octave))
        if "sus43" in card.templates and is_dominant(chord):
            sus = [chord.root, chord.root + iv.P4, chord.root + iv.P5, chord.root + iv.m7]
            raw.append(_stack_close(sus, octave))
        if (
            "quartal" in card.templates
            and iv.m3 in chord.intervals
            and iv.m7 in chord.intervals
            and iv.M9 in chord.intervals
        ):
            q = [
                chord.root,
                chord.root + iv.P4,
                chord.root + iv.m7,
                chord.root + iv.m3,
                chord.root + iv.P5,
            ]
            raw.append(_stack_close(q, octave, first_gap_min=5))
    seen: set[tuple[int, ...]] = set()
    good: list[tuple[SpelledPitch, ...]] = []
    for stack in raw:
        key = tuple(p.midi for p in stack)
        if key in seen or not valid(stack, chord, card):
            continue
        seen.add(key)
        good.append(stack)
    good.sort(key=lambda s: abs(sum(p.midi for p in s) / len(s) - center))
    return good[:24]
