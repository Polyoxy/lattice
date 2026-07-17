from __future__ import annotations

import io
import json
import sys
import tarfile
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lattice.model import DrumSound
from lattice.render.kits import KIT_KEYWORDS

API = "https://api.github.com/repos/Boochi44/free-drum-samples/contents"
OUT = Path(__file__).resolve().parents[1] / "assets" / "kit"

PIANO_URL = "https://freepats.zenvoid.org/Piano/YDP-GrandPiano/YDP-GrandPiano-SF2-20160804.tar.bz2"
PIANO_NAME = "YDP-GrandPiano-20160804.sf2"
PIANO_LICENSE = (
    "CC BY 3.0 - samples: Zenph Studios (Dr. Mikhail Krishtal) for OLPC / "
    "Dr. Richard Boulanger, cSounds.com; SF2 packaging: roberto@zenvoid.org, "
    "FreePats project. https://creativecommons.org/licenses/by/3.0/"
)
PIANO_OUT = Path(__file__).resolve().parents[1] / "assets" / "piano"


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "lattice-fetch-assets"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data: bytes = r.read()
        return data


def _walk(path: str = "") -> list[dict[str, str]]:
    entries = json.loads(_get(f"{API}/{path}" if path else API))
    files: list[dict[str, str]] = []
    for e in entries:
        if e["type"] == "dir":
            files.extend(_walk(e["path"]))
        elif e["name"].lower().endswith(".wav"):
            files.append(e)
    return files


def _fetch_piano() -> list[str]:
    PIANO_OUT.mkdir(parents=True, exist_ok=True)
    dest = PIANO_OUT / PIANO_NAME
    if dest.exists():
        return []
    with tarfile.open(fileobj=io.BytesIO(_get(PIANO_URL)), mode="r:bz2") as tar:
        member = next(m for m in tar.getmembers() if m.name.endswith(".sf2"))
        extracted = tar.extractfile(member)
        assert extracted is not None
        dest.write_bytes(extracted.read())
    return [f"- piano/{dest.name} ← {PIANO_URL} ({PIANO_LICENSE})"]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    files = _walk()
    manifest: list[str] = []
    for sound in DrumSound:
        dest = OUT / f"{sound.value}.wav"
        if dest.exists():
            continue
        hit = next(
            (
                f
                for kw in KIT_KEYWORDS[sound]
                for f in files
                if kw in f["name"].lower().replace("-", "_")
            ),
            None,
        )
        if hit is None:
            continue
        dest.write_bytes(_get(hit["download_url"]))
        manifest.append(
            f"- kit/{dest.name} ← {hit['download_url']} (CC0, Boochi44/free-drum-samples)"
        )
    from lattice.render.synth_perc import write_missing

    for name in write_missing(OUT):
        manifest.append(f"- kit/{name}.wav ← synthesized (CC0, lattice.render.synth_perc)")
    manifest.extend(_fetch_piano())
    misses = [s.value for s in DrumSound if not (OUT / f"{s.value}.wav").exists()]
    if manifest:
        mpath = OUT.parent / "MANIFEST.md"
        existing = mpath.read_text() if mpath.exists() else "# Assets\n\n"
        mpath.write_text(existing + "\n".join(manifest) + "\n")
    if misses:
        print(f"NO MATCH for: {', '.join(misses)}", file=sys.stderr)
        return 1
    print(f"kit complete at {OUT}")
    print(f"piano at {PIANO_OUT / PIANO_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
