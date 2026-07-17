from __future__ import annotations

from pathlib import Path
from typing import Final

from lattice.model import DrumSound

# Anchored to the repo root (uv editable src-layout install) so renders work
# from any cwd instead of only the checkout directory.
_KIT_DIR: Final = Path(__file__).resolve().parents[3] / "assets" / "kit"

KIT_KEYWORDS: Final[dict[DrumSound, tuple[str, ...]]] = {
    DrumSound.KICK: ("kick",),
    DrumSound.SNARE: ("snare",),
    DrumSound.RIM: ("rim", "sidestick"),
    DrumSound.CLAP: ("clap",),
    DrumSound.HAT_CLOSED: ("hat_closed", "closedhat", "closed_hat", "hihat", "hat"),
    DrumSound.HAT_OPEN: ("hat_open", "openhat", "open_hat"),
    DrumSound.RIDE: ("ride",),
    DrumSound.TOM_LO: ("tom_low", "tom_lo", "lowtom", "tom"),
    DrumSound.TOM_HI: ("tom_high", "tom_hi", "hightom", "high_tom"),
    DrumSound.BONGO: ("bongo", "conga"),
    DrumSound.SHAKER: ("shaker", "cabasa"),
    DrumSound.GHOST_KICK: ("kick",),
}


def load_kit(root: Path = _KIT_DIR) -> dict[DrumSound, Path]:
    kit: dict[DrumSound, Path] = {}
    missing: list[str] = []
    for sound in DrumSound:
        p = root / f"{sound.value}.wav"
        if p.exists():
            kit[sound] = p
        else:
            missing.append(sound.value)
    if missing:
        raise FileNotFoundError(f"kit at {root} missing: {', '.join(missing)}")
    return kit
