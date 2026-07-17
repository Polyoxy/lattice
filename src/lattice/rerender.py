from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import fields, replace
from pathlib import Path
from typing import Any, get_args, get_origin, get_type_hints

from lattice.api import make_beat
from lattice.beat import Beat
from lattice.cards import StyleCard, get_card
from lattice.render.engine import render_beat

_DRIFT_MESSAGE = (
    "{path}: rebuilt beat does not match the recorded beat.json (drift). "
    "This beat.json predates engine changes; re-render will differ from the "
    "original release. Pass --force to render anyway."
)


def _convert_field_value(hint: Any, value: Any) -> Any:
    if get_origin(hint) is not tuple:
        return value
    elem_hint = get_args(hint)[0]
    if get_origin(elem_hint) is tuple:
        return tuple(tuple(item) for item in value)
    return tuple(value)


def _reconstruct_card(card_data: dict[str, Any]) -> StyleCard:
    current = get_card(card_data["name"])
    hints = get_type_hints(StyleCard)
    kwargs = {
        f.name: _convert_field_value(hints[f.name], card_data[f.name])
        for f in fields(StyleCard)
        if f.name in card_data
    }
    return replace(current, **kwargs)


def _restrict_to_shape(value: Any, shape: Any) -> Any:
    if isinstance(shape, dict) and isinstance(value, dict):
        return {k: _restrict_to_shape(value[k], v) for k, v in shape.items() if k in value}
    if isinstance(shape, list) and isinstance(value, list) and len(shape) == len(value):
        return [_restrict_to_shape(v, s) for v, s in zip(value, shape)]
    return value


def rebuild(beat_json: Path, *, force: bool = False) -> Beat:
    data: dict[str, Any] = json.loads(Path(beat_json).read_text())
    card = _reconstruct_card(data["card"])
    index: int = data["index"]
    beat = make_beat(
        style=card, key=data["key"], bpm=data["bpm"], bars=data["bars"],
        n=index + 1, seed=data["seed"],
    )[index]
    rebuilt_data: dict[str, Any] = json.loads(beat.to_json())
    original_data: dict[str, Any] = dict(data)
    rebuilt_data.pop("engine", None)
    original_data.pop("engine", None)
    pre_bridge_original = "section_b" not in original_data
    drifted = _restrict_to_shape(rebuilt_data, original_data) != original_data
    if pre_bridge_original and rebuilt_data.get("section_b") is not None:
        drifted = True
    if drifted:
        message = _DRIFT_MESSAGE.format(path=beat_json)
        if not force:
            raise ValueError(message)
        print(f"warning: {message}", file=sys.stderr)
    return beat


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m lattice.rerender")
    parser.add_argument("song_dir", type=Path)
    parser.add_argument("out_dir", type=Path, nargs="?", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    song_dir: Path = args.song_dir
    out_dir: Path = args.out_dir if args.out_dir is not None else song_dir / "render"

    try:
        beat = rebuild(song_dir / "beat.json", force=args.force)
    except FileNotFoundError:
        print(f"{song_dir}: no beat.json found", file=sys.stderr)
        return 1
    except KeyError as exc:
        print(
            f"{song_dir / 'beat.json'}: missing or unknown field {exc.args[0]!r}",
            file=sys.stderr,
        )
        return 1
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    render_beat(beat, out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
