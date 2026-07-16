from __future__ import annotations

import numpy as np

from lattice.arrange import build_timeline
from lattice.beat import Beat
from lattice.cards import StyleCard, get_card
from lattice.groove.bass import bass_parts
from lattice.groove.drums import conductor_patterns, faiyaz_patterns
from lattice.groove.keys import keys_events
from lattice.groove.pocket import apply_pocket
from lattice.harmony.elaborate import elaborate
from lattice.harmony.grammar import Loop, candidate_loops
from lattice.harmony.score import loop_score, rank
from lattice.model import Role
from lattice.theory.key import Key, parse_key
from lattice.voicing.realize import realize


def _rng(seed: int, *key: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence(entropy=seed, spawn_key=key))


def _draw_key(card: StyleCard, rng: np.random.Generator) -> Key:
    if rng.random() < card.p_major_center:
        return parse_key(str(rng.choice(list(card.major_centers))))
    return parse_key(str(rng.choice(list(card.centers))))


def make_beat(
    style: str | StyleCard = "faiyaz",
    key: str | None = None,
    bpm: int | None = None,
    bars: int = 4,
    n: int = 5,
    seed: int = 0,
) -> list[Beat]:
    card = get_card(style) if isinstance(style, str) else style
    fixed_key = parse_key(key) if key is not None else None
    loops_cache: dict[Key, list[Loop]] = {}
    ranked_cache: dict[tuple[Key, int], list[Loop]] = {}
    beats: list[Beat] = []
    for i in range(n):
        rng = _rng(seed, i)
        k = fixed_key if fixed_key is not None else _draw_key(card, rng)
        b = bpm if bpm is not None else int(rng.integers(card.bpm_range[0], card.bpm_range[1] + 1))
        lengths = [ln for ln, _ in card.loop_len_weights]
        weights = [w for _, w in card.loop_len_weights]
        length = int(rng.choice(np.array(lengths), p=np.array(weights) / sum(weights)))
        if k not in loops_cache:
            loops_cache[k] = candidate_loops(card, k, bars)
        cache_key = (k, length)
        if cache_key not in ranked_cache:
            ranked_cache[cache_key] = rank(
                [lp for lp in loops_cache[k] if len(lp.items) == length], card, max(n, 1)
            )
        ranked = ranked_cache[cache_key]
        loop = ranked[i % len(ranked)]
        segments = elaborate(loop, card, rng)
        voicings = realize(segments, card)
        drums_gen = conductor_patterns if card.name in ("conductor", "molina") else faiyaz_patterns
        drums = drums_gen(card, bars, rng)
        if rng.random() < card.p_drumless:
            drums = {v: {r: () for r in variant} for v, variant in drums.items()}
        shared = {
            **bass_parts(segments, card, rng),
            Role.KEYS: keys_events(segments, voicings, bars, card, rng),
        }
        parts_a, report = apply_pocket({**drums["A"], **shared}, card, b, _rng(seed, i, 1))
        parts_b, _ = apply_pocket({**drums["B"], **shared}, card, b, _rng(seed, i, 1))
        timeline = build_timeline(card, bars, b, rng)
        beats.append(
            Beat(
                card=card, key=k, bpm=b, bars=bars, seed=seed, index=i, loop=loop,
                segments=segments, voicings=voicings, parts_a=parts_a, parts_b=parts_b,
                timeline=timeline, pocket=report, score=loop_score(loop, card),
            )
        )
    return beats
