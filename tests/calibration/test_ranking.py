import pytest

from lattice.cards import FAIYAZ, get_card
from lattice.harmony.functions import build_function
from lattice.harmony.grammar import Loop, candidate_loops
from lattice.harmony.score import loop_score
from lattice.theory.key import parse_key
from tests.calibration.corpus import CORPUS


@pytest.mark.slow
def test_every_documented_loop_ranks_top_5_percent() -> None:
    failures: list[str] = []
    for r in CORPUS:
        key = parse_key(r.key)
        ref = Loop(key, tuple(build_function(key, n) for n in r.functions), bars=4)
        pool = candidate_loops(FAIYAZ, key, bars=4)
        scores = sorted((loop_score(lp, FAIYAZ) for lp in pool), reverse=True)
        ref_score = loop_score(ref, FAIYAZ)
        rank_pos = sum(1 for s in scores if s > ref_score)
        percentile = 1 - rank_pos / len(scores)
        if percentile < 0.95:
            failures.append(f"{r.name}: {percentile:.1%} (pos {rank_pos}/{len(scores)})")
    assert not failures, "; ".join(failures)


@pytest.mark.slow
def test_ballroom_period_progressions_rank_top_decile() -> None:
    card = get_card("ballroom")
    key = parse_key("F")
    pool = [lp for lp in candidate_loops(card, key, 4) if len(lp.items) == 4]
    assert pool
    scores = sorted((loop_score(lp, card) for lp in pool), reverse=True)
    cutoff = scores[max(0, len(scores) // 10 - 1)]
    for names in [
        ("I6", "vi7", "ii7maj", "V7maj"),
        ("I6", "#idim7", "ii7maj", "V7maj"),
        ("iii7", "VI7", "ii7maj", "V7maj"),
    ]:
        match = [lp for lp in pool if lp.names() == names]
        assert match, names
        assert loop_score(match[0], card) >= cutoff, names
