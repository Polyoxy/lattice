import json
from pathlib import Path

import pytest

from lattice import make_beat, rerender
from lattice.rerender import _convert_field_value, main, rebuild

_WHITE_GLOVES_FIXTURE = Path(__file__).parent / "fixtures" / "white_gloves_beat.json"


def test_rebuild_round_trips_exactly(tmp_path: Path) -> None:
    original = make_beat(style="molina", key="Cm", bpm=84, bars=2, n=2, seed=9)[1]
    original.save(str(tmp_path))
    rebuilt = rebuild(tmp_path / "beat.json")
    assert rebuilt.to_json() == original.to_json()


def test_rebuild_round_trips_exactly_for_chase(tmp_path: Path) -> None:
    original = make_beat(style="chase", key="Dm", bpm=160, bars=2, n=1, seed=5)[0]
    original.save(str(tmp_path))
    rebuilt = rebuild(tmp_path / "beat.json")
    assert rebuilt.to_json() == original.to_json()


def test_rebuild_tolerates_roles_the_json_predates(tmp_path: Path) -> None:
    # Frozen copy of a released beat.json from before Role.LEAD existed. Its
    # timeline muted lists predate the enum growing, so this is the
    # cross-commit regression tripwire the drift guard needs: rebuilding a
    # real released track must not false-positive as it did before the
    # rebuilt-side role filtering (Finding 1).
    (tmp_path / "beat.json").write_text(_WHITE_GLOVES_FIXTURE.read_text())
    rebuild(tmp_path / "beat.json")


def test_rebuild_detects_drift(tmp_path: Path) -> None:
    original = make_beat(style="faiyaz", key="Am", bpm=72, bars=2, n=1, seed=1)[0]
    original.save(str(tmp_path))
    data = json.loads((tmp_path / "beat.json").read_text())
    data["pocket"]["swing"] = 0.99
    (tmp_path / "beat.json").write_text(json.dumps(data, sort_keys=True))
    with pytest.raises(ValueError, match="drift"):
        rebuild(tmp_path / "beat.json")


def test_rebuild_tolerates_engine_version_bump(tmp_path: Path) -> None:
    original = make_beat(style="conductor", key="Cm", bpm=90, bars=2, n=1, seed=6)[0]
    original.save(str(tmp_path))
    data = json.loads((tmp_path / "beat.json").read_text())
    data["engine"] = "0.0.1-different"
    (tmp_path / "beat.json").write_text(json.dumps(data, sort_keys=True))
    rebuilt = rebuild(tmp_path / "beat.json")
    rebuilt_data = json.loads(rebuilt.to_json())
    original_data = json.loads(original.to_json())
    assert rebuilt_data["loop"] == original_data["loop"]
    assert rebuilt_data["pocket"] == original_data["pocket"]
    assert rebuilt_data["segments"] == original_data["segments"]


def test_rebuild_falls_back_to_registered_card_for_missing_fields(tmp_path: Path) -> None:
    original = make_beat(style="tunisia", key="Dm", bpm=140, bars=4, n=1, seed=3)[0]
    original.save(str(tmp_path))
    data = json.loads((tmp_path / "beat.json").read_text())
    for missing in (
        "voicing_density", "has_bridge", "bridge_function_pool",
        "bridge_major_function_pool", "bridge_len_weights",
    ):
        del data["card"][missing]
    (tmp_path / "beat.json").write_text(json.dumps(data, sort_keys=True))
    rebuilt = rebuild(tmp_path / "beat.json")
    assert rebuilt.to_json() == original.to_json()


def test_rebuild_force_returns_beat_despite_drift(tmp_path: Path) -> None:
    original = make_beat(style="faiyaz", key="Am", bpm=72, bars=2, n=1, seed=1)[0]
    original.save(str(tmp_path))
    data = json.loads((tmp_path / "beat.json").read_text())
    data["pocket"]["swing"] = 0.99
    (tmp_path / "beat.json").write_text(json.dumps(data, sort_keys=True))
    rebuilt = rebuild(tmp_path / "beat.json", force=True)
    assert rebuilt.card.name == "faiyaz"


def test_main_defaults_out_dir_to_song_dir_render(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    beat = make_beat(style="faiyaz", key="Am", bpm=72, bars=1, n=1, seed=2)[0]
    beat.save(str(tmp_path))
    calls: list[tuple[object, object]] = []
    monkeypatch.setattr(rerender, "render_beat", lambda b, out: calls.append((b, out)))
    code = main([str(tmp_path)])
    assert code == 0
    assert calls and calls[0][1] == tmp_path / "render"


def test_main_uses_explicit_out_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    beat = make_beat(style="faiyaz", key="Am", bpm=72, bars=1, n=1, seed=2)[0]
    beat.save(str(tmp_path))
    out_dir = tmp_path / "custom"
    calls: list[tuple[object, object]] = []
    monkeypatch.setattr(rerender, "render_beat", lambda b, out: calls.append((b, out)))
    code = main([str(tmp_path), str(out_dir)])
    assert code == 0
    assert calls and calls[0][1] == out_dir


def test_main_blocks_on_drift_without_force(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    beat = make_beat(style="faiyaz", key="Am", bpm=72, bars=1, n=1, seed=2)[0]
    beat.save(str(tmp_path))
    data = json.loads((tmp_path / "beat.json").read_text())
    data["pocket"]["swing"] = 0.99
    (tmp_path / "beat.json").write_text(json.dumps(data, sort_keys=True))
    calls: list[object] = []
    monkeypatch.setattr(rerender, "render_beat", lambda b, out: calls.append(out))
    code = main([str(tmp_path)])
    assert code == 1
    assert not calls
    err = capsys.readouterr().err
    assert "predates engine changes" in err
    assert "--force" in err


def test_main_force_flag_renders_despite_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    beat = make_beat(style="faiyaz", key="Am", bpm=72, bars=1, n=1, seed=2)[0]
    beat.save(str(tmp_path))
    data = json.loads((tmp_path / "beat.json").read_text())
    data["pocket"]["swing"] = 0.99
    (tmp_path / "beat.json").write_text(json.dumps(data, sort_keys=True))
    calls: list[object] = []
    monkeypatch.setattr(rerender, "render_beat", lambda b, out: calls.append(out))
    code = main([str(tmp_path), "--force"])
    assert code == 0
    assert calls


def test_main_end_to_end_real_render(tmp_path: Path) -> None:
    from lattice.render.kits import load_kit

    try:
        load_kit()
    except FileNotFoundError:
        pytest.skip("kit not fetched")
    beat = make_beat(style="faiyaz", key="Am", bpm=90, bars=1, n=1, seed=8)[0]
    beat.save(str(tmp_path))
    code = main([str(tmp_path)])
    assert code == 0
    assert (tmp_path / "render" / "master.wav").exists()
    assert (tmp_path / "render" / "mix.wav").exists()


def test_pre_bridge_json_rejects_rebuilt_bridge(tmp_path: Path) -> None:
    from lattice.cards import FAIYAZ

    card = FAIYAZ.override(
        has_bridge=True,
        bridge_function_pool=("iv7", "bVII9", "v7", "i7"),
        bridge_major_function_pool=("IVmaj7", "V7maj", "Imaj7"),
        bridge_len_weights=((3, 0.5), (4, 0.5)),
    )
    original = make_beat(style=card, key="Am", bpm=80, bars=2, n=1, seed=4)[0]
    original.save(str(tmp_path))
    data = json.loads((tmp_path / "beat.json").read_text())
    del data["section_b"]
    (tmp_path / "beat.json").write_text(json.dumps(data, sort_keys=True))
    with pytest.raises(ValueError, match="drift"):
        rebuild(tmp_path / "beat.json")


def test_cli_missing_song_dir_exits_cleanly(tmp_path: Path) -> None:
    from lattice.rerender import main

    code = main([str(tmp_path / "nope")])
    assert code == 1


def test_main_unknown_card_name_exits_cleanly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    beat = make_beat(style="faiyaz", key="Am", bpm=72, bars=1, n=1, seed=2)[0]
    beat.save(str(tmp_path))
    data = json.loads((tmp_path / "beat.json").read_text())
    data["card"]["name"] = "no_such_card"
    (tmp_path / "beat.json").write_text(json.dumps(data, sort_keys=True))
    calls: list[object] = []
    monkeypatch.setattr(rerender, "render_beat", lambda b, out: calls.append(out))
    code = main([str(tmp_path)])
    assert code == 1
    assert not calls
    err = capsys.readouterr().err
    assert "no_such_card" in err
    assert "Traceback" not in err


def test_convert_field_value_recurses_three_deep() -> None:
    hint = tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]
    value = [[[0, -3], [0, 2]], [[1, -4, 1], [0, 1, 2]]]
    out = _convert_field_value(hint, value)
    assert out == (((0, -3), (0, 2)), ((1, -4, 1), (0, 1, 2)))
    assert isinstance(out[0][0], tuple)
