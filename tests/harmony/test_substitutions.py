import pytest

from lattice.cards import FAIYAZ, MOLINA
from lattice.harmony.substitutions import (
    backdoor,
    passing_dim,
    related_ii,
    secondary_dominant,
    subs_for,
    tritone_sub,
)
from lattice.theory.chord import build, symbol
from lattice.theory.key import parse_key
from lattice.theory.pitch import parse_tpc


def test_secondary_dominant_of_iv_in_am_is_a7() -> None:
    dm = build(parse_tpc("D"), "m7")
    sub = secondary_dominant(dm)
    assert symbol(sub.chord) == "A7"
    assert sub.label == "V7/Dm7"


def test_tritone_sub_of_g7_is_db7() -> None:
    g7 = build(parse_tpc("G"), "7")
    assert symbol(tritone_sub(g7).chord) == "Db7"
    with pytest.raises(ValueError):
        tritone_sub(build(parse_tpc("G"), "m7"))


def test_backdoor_in_c_is_bb7() -> None:
    assert symbol(backdoor(parse_key("C")).chord) == "Bb7"


def test_related_ii_of_g7_is_dm7() -> None:
    assert symbol(related_ii(build(parse_tpc("G"), "7")).chord) == "Dm7"


def test_passing_dim_fills_whole_step() -> None:
    c = build(parse_tpc("C"), "maj7")
    d = build(parse_tpc("D"), "m7")
    sub = passing_dim(c, d)
    assert sub is not None and symbol(sub.chord) == "C#dim7"
    assert passing_dim(c, build(parse_tpc("F"), "maj7")) is None


def test_card_gating() -> None:
    key = parse_key("Am")
    prev = build(parse_tpc("A"), "m7")
    target = build(parse_tpc("D"), "m7")
    faiyaz_subs = subs_for(FAIYAZ, key, prev, target)
    molina_subs = subs_for(MOLINA, key, prev, target)
    assert all("tritone" not in s.label for s in faiyaz_subs)
    assert any("tritone" in s.label for s in molina_subs)
    assert len(molina_subs) > len(faiyaz_subs)
