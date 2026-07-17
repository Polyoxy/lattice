import numpy as np

from lattice.arrange import build_timeline
from lattice.cards import FAIYAZ, get_card
from lattice.model import Role, bar_s


def test_duration_lands_in_card_band() -> None:
    for seed in range(20):
        t = build_timeline(FAIYAZ, bars=4, bpm=72, rng=np.random.default_rng(seed))
        seconds = t.total_cycles * 4 * bar_s(72)
        assert 80 <= seconds <= 165


def test_bookends_are_keys_only() -> None:
    t = build_timeline(FAIYAZ, bars=4, bpm=72, rng=np.random.default_rng(0))
    first, last = t.sections[0], t.sections[-1]
    assert first.kind == "intro" and last.kind == "outro"
    for s in (first, last):
        assert Role.KEYS not in s.muted
        assert Role.KICK in s.muted and Role.SUB in s.muted


def test_transpose_carries_from_final_content_to_outro() -> None:
    card = FAIYAZ.override(p_transpose_event=1.0)
    for seed in range(30):
        t = build_timeline(card, bars=4, bpm=72, rng=np.random.default_rng(seed))
        stamped = [i for i, s in enumerate(t.sections) if s.transpose]
        assert len(stamped) >= 1
        first = stamped[0]
        assert t.sections[first].kind in ("a", "b")
        for i, s in enumerate(t.sections):
            if i >= first:
                assert s.transpose == card.transpose_semitones
            else:
                assert s.transpose == 0


def test_all_sections_at_least_one_cycle_and_kinds_valid() -> None:
    for seed in range(10):
        t = build_timeline(FAIYAZ, bars=4, bpm=90, rng=np.random.default_rng(seed))
        assert all(s.cycles >= 1 for s in t.sections)
        assert {s.kind for s in t.sections} <= {"intro", "a", "b", "drop", "outro"}


def test_aaba_pattern_cycles() -> None:
    card = get_card("ballroom")
    tl = build_timeline(card, 4, 112, np.random.default_rng(3))
    body = [s.kind for s in tl.sections if s.kind in ("a", "b")]
    pattern = ("a", "a", "b", "a")
    assert all(k == pattern[i % 4] for i, k in enumerate(body))


def test_pad_enters_after_first_body_section() -> None:
    card = get_card("ballroom")
    tl = build_timeline(card, 4, 112, np.random.default_rng(3))
    body = [s for s in tl.sections if s.kind not in ("intro", "outro")]
    assert Role.PAD in body[0].muted
    assert all(Role.PAD not in s.muted for s in body[1:] if s.kind in ("a", "b"))


def test_default_cards_timeline_unchanged() -> None:
    for name in ("faiyaz", "tunisia"):
        card = get_card(name)
        tl = build_timeline(card, 4, 90, np.random.default_rng(3))
        assert all(Role.PAD not in s.muted or s.kind in ("intro", "outro") for s in tl.sections)
