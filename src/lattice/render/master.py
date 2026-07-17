from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Final

_SATURATOR_URI: Final = "http://calf.sourceforge.net/plugins/Saturator"
_LIMITER_URI: Final = "http://gareus.org/oss/lv2/dpl#stereo"
_SATURATOR_NAME: Final = "saturator"
_LIMITER_NAME: Final = "limiter"


def discover_lv2() -> dict[str, str]:
    found: dict[str, str] = {}
    try:
        result = subprocess.run(["lv2ls"], check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return found
    dpl_fallback: str | None = None
    for line in result.stdout.splitlines():
        uri = line.strip()
        if not uri:
            continue
        if uri == _SATURATOR_URI:
            found[_SATURATOR_NAME] = uri
        elif uri == _LIMITER_URI:
            found[_LIMITER_NAME] = uri
        elif dpl_fallback is None and "dpl" in uri:
            dpl_fallback = uri
    if _LIMITER_NAME not in found and dpl_fallback is not None:
        found[_LIMITER_NAME] = dpl_fallback
    return found


def _apply(in_path: Path, out_path: Path, uri: str) -> bool:
    try:
        subprocess.run(
            ["lv2apply", "-i", str(in_path), "-o", str(out_path), uri],
            check=True, capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        print(f"lv2 plugin unavailable, skipping: {uri}")
        return False
    return True


def master(mix_path: Path, out_path: Path) -> Path:
    found = discover_lv2()
    current = mix_path
    saturator_staged = out_path.with_name(f"{out_path.stem}_saturator.wav")
    limiter_staged = out_path.with_name(f"{out_path.stem}_limiter.wav")

    if _SATURATOR_NAME in found:
        if _apply(current, saturator_staged, found[_SATURATOR_NAME]):
            current = saturator_staged
    else:
        print("lv2 plugin not found, skipping: saturator")

    if _LIMITER_NAME in found:
        if _apply(current, limiter_staged, found[_LIMITER_NAME]):
            current = limiter_staged
    else:
        print("lv2 plugin not found, skipping: limiter")

    try:
        # dither must run last: an explicit dither suppresses sox's automatic one,
        # so anything after it (fade, gain) would requantize undithered.
        # -R fixes the dither PRNG seed for repeatable output.
        subprocess.run(
            [
                "sox", "-R", str(current), "-b", "16", str(out_path),
                "rate", "44100", "fade", "t", "0.01", "0", "0.05", "gain", "-n", "-1.0", "dither",
            ],
            check=True, capture_output=True,
        )
    finally:
        saturator_staged.unlink(missing_ok=True)
        limiter_staged.unlink(missing_ok=True)
    return out_path
