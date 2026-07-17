from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

_SR = 44100


def _hp(x: np.ndarray, cutoff: float) -> np.ndarray:
    rc = 1.0 / (2 * np.pi * cutoff)
    alpha = rc / (rc + 1.0 / _SR)
    y = np.zeros_like(x)
    prev_x = 0.0
    prev_y = 0.0
    for i in range(len(x)):
        y[i] = alpha * (prev_y + x[i] - prev_x)
        prev_x = x[i]
        prev_y = y[i]
    return y


def _write(path: Path, sig: np.ndarray) -> None:
    peak = float(np.max(np.abs(sig))) or 1.0
    pcm = np.clip(sig / peak * 0.9, -1.0, 1.0)
    data = (pcm * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(_SR)
        w.writeframes(data.tobytes())


def _shaker(rng: np.random.Generator) -> np.ndarray:
    out = np.zeros(int(_SR * 0.25))
    for start in (0.0, 0.11):
        n = int(_SR * 0.09)
        i0 = int(start * _SR)
        noise = rng.standard_normal(n)
        env = np.exp(-np.linspace(0, 8, n))
        out[i0 : i0 + n] += _hp(noise, 5500.0) * env
    return out


def _bongo(rng: np.random.Generator) -> np.ndarray:
    n = int(_SR * 0.18)
    t = np.arange(n) / _SR
    body = np.sin(2 * np.pi * 320.0 * t) * np.exp(-t * 22.0)
    click = np.zeros(n)
    cn = int(_SR * 0.003)
    click[:cn] = _hp(rng.standard_normal(cn), 2000.0) * np.exp(-np.linspace(0, 6, cn))
    return body + click * 0.6


def _ride(rng: np.random.Generator) -> np.ndarray:
    n = int(_SR * 1.4)
    t = np.arange(n) / _SR
    partials = np.zeros(n)
    for ratio in (1.0, 2.7, 4.2, 5.4, 6.8, 8.1):
        partials += np.sin(2 * np.pi * 380.0 * ratio * t)
    env = np.exp(-t * 3.2)
    noise = _hp(rng.standard_normal(n), 6000.0) * 0.25
    return _hp((partials / 6.0 + noise) * env, 3000.0)


def _brush_tap(rng: np.random.Generator) -> np.ndarray:
    n = int(_SR * 0.09)
    noise = _hp(rng.standard_normal(n), 1500.0)
    env = np.exp(-np.linspace(0, 11, n))
    return noise * env


def _brush_swirl(rng: np.random.Generator) -> np.ndarray:
    n = int(_SR * 0.9)
    t = np.arange(n) / _SR
    noise = _hp(rng.standard_normal(n), 2500.0)
    breath = 0.6 + 0.4 * np.sin(2 * np.pi * 1.1 * t)
    attack = np.minimum(t / 0.18, 1.0)
    decay = np.exp(-np.maximum(t - 0.55, 0.0) * 9.0)
    return noise * breath * attack * decay


def _feather(rng: np.random.Generator) -> np.ndarray:
    n = int(_SR * 0.12)
    t = np.arange(n) / _SR
    thump = np.sin(2 * np.pi * 55.0 * t) * np.exp(-t * 40.0)
    return thump + _hp(rng.standard_normal(n), 900.0) * np.exp(-t * 120.0) * 0.08


def _chick(rng: np.random.Generator) -> np.ndarray:
    n = int(_SR * 0.05)
    noise = _hp(rng.standard_normal(n), 6500.0)
    return noise * np.exp(-np.linspace(0, 14, n))


_GENERATORS = {
    "shaker": _shaker, "bongo": _bongo, "ride": _ride,
    "brush_tap": _brush_tap, "brush_swirl": _brush_swirl,
    "feather": _feather, "chick": _chick,
}


def write_missing(root: Path) -> list[str]:
    root.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name, gen in _GENERATORS.items():
        dest = root / f"{name}.wav"
        if dest.exists():
            continue
        _write(dest, gen(np.random.default_rng(_SEEDS[name])))
        written.append(name)
    return written


_SEEDS = {
    "shaker": 101, "bongo": 202, "ride": 303,
    "brush_tap": 404, "brush_swirl": 505, "feather": 606, "chick": 707,
}
