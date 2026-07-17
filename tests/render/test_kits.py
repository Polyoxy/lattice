from pathlib import Path

import pytest

from lattice.model import DrumSound
from lattice.render.kits import KIT_KEYWORDS, load_kit


def test_every_drumsound_has_keywords() -> None:
    assert set(KIT_KEYWORDS) == set(DrumSound)
    assert all(KIT_KEYWORDS[s] for s in DrumSound)


def test_load_kit_reads_a_complete_directory(tmp_path: Path) -> None:
    for sound in DrumSound:
        (tmp_path / f"{sound.value}.wav").write_bytes(b"RIFF")
    kit = load_kit(tmp_path)
    assert set(kit) == set(DrumSound)
    assert kit[DrumSound.KICK].name == "kick.wav"


def test_load_kit_names_missing_sounds(tmp_path: Path) -> None:
    (tmp_path / "kick.wav").write_bytes(b"RIFF")
    with pytest.raises(FileNotFoundError, match="snare"):
        load_kit(tmp_path)
