from __future__ import annotations

import numpy as np

from lattice.arrange import build_timeline
from lattice.beat import Beat
from lattice.cards import StyleCard, get_card
from lattice.groove.bass import bass_parts
from lattice.groove.drums import ballroom_patterns, conductor_patterns, faiyaz_patterns
from lattice.groove.keys import keys_events
from lattice.groove.pocket import apply_pocket
from lattice.groove.strings import pad_events
from lattice.harmony.elaborate import elaborate
from lattice.harmony.grammar import Loop, candidate_loops
from lattice.harmony.score import contrast, loop_score, rank
from lattice.model import Role
from lattice.section import SectionRender
from lattice.theory.key import Key, key_name, parse_key
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
    if bpm is not None and bpm < 20:
        raise ValueError("bpm must be >= 20")
    if bars < 1:
        raise ValueError("bars must be >= 1")
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
        if not ranked:
            raise ValueError(f"no loops of length {length} for {key_name(k)} with card {card.name}")
        loop = ranked[i % len(ranked)]
        segments = elaborate(loop, card, rng)
        voicings = realize(segments, card)
        _drum_gens = {
            "conductor": conductor_patterns,
            "molina": conductor_patterns,
            "ballroom": ballroom_patterns,
        }
        drums_gen = _drum_gens.get(card.name, faiyaz_patterns)
        drums = drums_gen(card, bars, rng)
        if rng.random() < card.p_drumless:
            drums = {v: {r: () for r in variant} for v, variant in drums.items()}
        shared = {
            **bass_parts(segments, card, rng),
            Role.KEYS: keys_events(segments, voicings, bars, card, rng),
        }
        if card.has_strings:
            shared[Role.PAD] = pad_events(segments, voicings, bars)
        parts_a, report = apply_pocket({**drums["A"], **shared}, card, b, _rng(seed, i, 1))
        parts_b, _ = apply_pocket({**drums["B"], **shared}, card, b, _rng(seed, i, 1))
        section_b = None
        if card.has_bridge:
            bridge_card = card.override(
                function_pool=card.bridge_function_pool,
                major_function_pool=card.bridge_major_function_pool,
                loop_len_weights=card.bridge_len_weights,
            )
            groove_card = (
                card.override(bass_feel=card.bridge_bass_feel)
                if card.bridge_bass_feel else card
            )
            bl = [ln for ln, _ in card.bridge_len_weights]
            bw = [w for _, w in card.bridge_len_weights]
            b_length = int(rng.choice(np.array(bl), p=np.array(bw) / sum(bw)))
            bridge_pool = [
                lp for lp in candidate_loops(bridge_card, k, bars) if len(lp.items) == b_length
            ]
            if not bridge_pool:
                raise ValueError(f"no bridge loops of length {b_length} for {key_name(k)}")
            b_loop = max(
                bridge_pool, key=lambda lp: loop_score(lp, bridge_card) + contrast(loop, lp)
            )
            b_segments = elaborate(b_loop, bridge_card, rng)
            seed_from = voicings[-1] if voicings else None
            b_voicings = realize(b_segments, card, seed_from=seed_from)
            b_drums = drums_gen(bridge_card, bars, rng)
            if rng.random() < card.p_drumless:
                b_drums = {v: {r: () for r in variant} for v, variant in b_drums.items()}
            b_shared = {
                **bass_parts(b_segments, groove_card, rng),
                Role.KEYS: keys_events(b_segments, b_voicings, bars, card, rng),
            }
            if card.has_strings:
                b_shared[Role.PAD] = pad_events(b_segments, b_voicings, bars)
            b_parts_a, _ = apply_pocket({**b_drums["A"], **b_shared}, card, b, _rng(seed, i, 2))
            b_parts_b, _ = apply_pocket({**b_drums["B"], **b_shared}, card, b, _rng(seed, i, 2))
            section_b = SectionRender(b_loop, b_segments, b_voicings, b_parts_a, b_parts_b)
        timeline = build_timeline(card, bars, b, rng)
        beats.append(
            Beat(
                card=card, key=k, bpm=b, bars=bars, seed=seed, index=i, loop=loop,
                segments=segments, voicings=voicings, parts_a=parts_a, parts_b=parts_b,
                timeline=timeline, pocket=report, score=loop_score(loop, card),
                section_b=section_b,
            )
        )
    return beats
