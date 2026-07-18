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
    args = get_args(hint)
    elem_hint = args[0]
    if get_origin(elem_hint) is tuple:
        return tuple(_convert_field_value(elem_hint, item) for item in value)
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


def _known_role_names(original_data: dict[str, Any]) -> set[str]:
    """Role-name vocabulary the original json actually exercises.

    `beat.py` serializes each timeline section's `muted` from live `Role` enum
    membership, so a role added after a beat.json was released (LEAD today,
    more later) mutes unconditionally in the rebuild even though the original
    render never emitted it and never muted it. A role this json never
    mentions anywhere cannot change what it renders.
    """
    known = set(original_data["parts_a"]) | set(original_data["parts_b"])
    section_b = original_data.get("section_b")
    if section_b is not None:
        known |= set(section_b["parts_a"]) | set(section_b["parts_b"])
    for section in original_data["timeline"]:
        known.update(section["muted"])
    return known


def _restrict_muted_to_known_roles(
    rebuilt_data: dict[str, Any], known_roles: set[str]
) -> dict[str, Any]:
    """Drop roles the original json never knew about from the rebuild's mutes.

    `_restrict_to_shape` recurses element-wise on lists only when lengths
    match, so it cannot mask a newer Role enum member inflating a mute list
    beyond the original's length — that reads as drift on every released
    beat.json once the enum grows. Filtering rebuilt_data first keeps the
    lengths (and drift comparison) honest.
    """
    restricted_timeline = [
        {**section, "muted": [r for r in section["muted"] if r in known_roles]}
        for section in rebuilt_data["timeline"]
    ]
    return {**rebuilt_data, "timeline": restricted_timeline}


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
    rebuilt_data = _restrict_muted_to_known_roles(rebuilt_data, _known_role_names(original_data))
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
