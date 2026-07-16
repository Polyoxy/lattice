from lattice.cards import FAIYAZ
from lattice.harmony.grammar import expressible
from lattice.theory.key import parse_key
from tests.calibration.corpus import CORPUS


def test_corpus_coverage_at_least_90_percent() -> None:
    misses = [
        r.name
        for r in CORPUS
        if not expressible(FAIYAZ, parse_key(r.key), r.functions)
    ]
    coverage = 1 - len(misses) / len(CORPUS)
    assert coverage >= 0.9, f"coverage {coverage:.0%}, misses: {misses}"
