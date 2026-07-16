import pytest

from lattice.cards import FAIYAZ
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
