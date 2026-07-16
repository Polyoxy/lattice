from pathlib import Path

from lattice import make_beat
from lattice.section import SectionRender

_FIXTURE = Path(__file__).parent / "fixtures" / "faiyaz_seed7.mid"


def test_existing_cards_have_no_bridge() -> None:
    from lattice.cards import CONDUCTOR, FAIYAZ, MOLINA

    assert not FAIYAZ.has_bridge
    assert not CONDUCTOR.has_bridge
    assert not MOLINA.has_bridge
    assert FAIYAZ.bridge_function_pool == ()


def test_section_render_constructs() -> None:
    from lattice.harmony.functions import build_function
    from lattice.harmony.grammar import Loop
    from lattice.theory.key import parse_key

    key = parse_key("Am")
    loop = Loop(key, (build_function(key, "i7"),), bars=4)
    sr = SectionRender(loop=loop, segments=(), voicings=(), parts_a={}, parts_b={})
    assert sr.loop is loop


def test_faiyaz_golden_midi_unchanged(tmp_path: Path) -> None:
    beat = make_beat(style="faiyaz", key="C#m", bpm=72, bars=4, n=1, seed=7)[0]
    out = tmp_path / "check.mid"
    beat.to_midi(str(out))
    assert out.read_bytes() == _FIXTURE.read_bytes()


def test_unrolled_routes_bridge_to_b_sections() -> None:
    from lattice.harmony.functions import build_function
    from lattice.harmony.grammar import Loop
    from lattice.model import Event, Role, Section, Timeline
    from lattice.section import SectionRender

    a_ev = (Event(0, 480, 90, pitch=57),)
    b_ev = (Event(0, 480, 90, pitch=62),)
    from lattice.theory.key import parse_key

    kk = parse_key("Am")
    loop = Loop(kk, (build_function(kk, "i7"),), bars=1)
    a_parts = {Role.KEYS: a_ev}
    sr = SectionRender(loop=loop, segments=(), voicings=(), parts_a={Role.KEYS: b_ev}, parts_b={})
    timeline = Timeline((Section("a", 1), Section("b", 1)))
    from lattice.beat import Beat
    from lattice.groove.pocket import PocketReport

    beat = Beat(
        card=__import__("lattice.cards", fromlist=["FAIYAZ"]).FAIYAZ, key=kk, bpm=72, bars=1,
        seed=0, loop=loop, segments=(), voicings=(), parts_a=a_parts, parts_b={},
        timeline=timeline, pocket=PocketReport(0.5, 0.0, 0.0, 4.0), score=0.0, section_b=sr,
    )
    events = beat.unrolled()[Role.KEYS]
    pitches_by_tick = {e.tick: e.pitch for e in events}
    assert pitches_by_tick[0] == 57
    assert pitches_by_tick[1 * 3840] == 62


def test_section_b_none_is_backward_compatible() -> None:
    beat = make_beat(style="faiyaz", key="Am", bpm=72, bars=2, n=1, seed=5)[0]
    assert beat.section_b is None
    import json

    assert json.loads(beat.to_json())["section_b"] is None


def test_bridge_card_produces_section_b_and_timeline_b() -> None:
    from lattice.cards import FAIYAZ

    card = FAIYAZ.override(
        has_bridge=True,
        bridge_function_pool=("iv7", "bVII9", "v7", "i7"),
        bridge_major_function_pool=("IVmaj7", "V7maj", "Imaj7"),
        bridge_len_weights=((3, 0.5), (4, 0.5)),
    )
    beat = make_beat(style=card, key="Am", bpm=80, bars=4, n=1, seed=4)[0]
    assert beat.section_b is not None
    assert beat.section_b.loop.names() != beat.loop.names()
    assert any(s.kind == "b" for s in beat.timeline.sections)


def test_bridge_gating_leaves_single_loop_cards_byte_identical(tmp_path: Path) -> None:
    beat = make_beat(style="faiyaz", key="C#m", bpm=72, bars=4, n=1, seed=7)[0]
    out = tmp_path / "again.mid"
    beat.to_midi(str(out))
    assert out.read_bytes() == _FIXTURE.read_bytes()
