# Audio Engine for Lattice on lexy — Research Brief

Research input for the Lattice spec. Compiled 2026-07-15. All "verified" claims were
tested on lexy itself during research.

## Machine reality (verified on this box)

Ubuntu 24.04.4 headless, Python 3.12.3, pipewire 1.0.5 with one Built-in Audio ALSA sink
(**currently muted** — `wpctl set-mute @DEFAULT_AUDIO_SINK@ 0`), 3.6GB RAM (~2.5GB
available), and the single most consequential fact: **the Pentium Gold 6405U has no
AVX/AVX2/FMA. `/proc/cpuinfo` shows SSE4.2 as the SIMD ceiling** (Intel fuses AVX off on
Pentium/Celeron SKUs).

## Bottom line

**SuperCollider's `scsynth` from apt, driven from Python by `supriya`, offline-first (NRT
rendering), with identical SynthDefs usable in realtime later.** Csound 6.18 + `libcsound`
is the credible runner-up. fluidsynth + jRhodes3 soundfont is the 30-minute MVP for the
electric-piano voice. Everything shipping DSP as pip binary wheels is dead on this CPU.

## The AVX landmine (verified locally)

- **pedalboard 0.9.24** (Spotify): `import pedalboard` → **Illegal instruction (core
  dumped)**. Unusable as shipped.
- **DawDreamer 0.8.3**: import succeeds; constructing `RenderEngine` / rendering →
  **SIGILL, exit 132**. Unusable. (Otherwise it was exactly the right tool — ISMIR 2021,
  "Python symbolic → offline audio on a server": https://github.com/DBraun/DawDreamer)
- **signalflow 0.5.4**: aarch64-only manylinux wheels for current release — no x86_64
  wheel at all (verified via PyPI JSON).
- **pyo 1.0.5**: last release 2023, no cp312 wheels. Stale.
- **supriya 26.3b0** (2026-03-18): pure-Python wheel, **installs clean on 3.12 and
  compiled a SynthDef to 421 bytes of scsynth bytecode with no SuperCollider installed**
  (verified). https://pypi.org/project/supriya/

Debian/Ubuntu packages are compiled for the amd64 baseline (SSE2), so apt-installed
engines cannot hit this. Third-party plugin binaries (Surge XT debs, Airwindows builds)
are the same roulette — assume broken until proven otherwise on this CPU.

## Engine-by-engine

### SuperCollider (scsynth) + supriya — the recommendation
- **Headless: genuinely.** CLI UDP/TCP server. With `--no-install-recommends`,
  `supercollider-server` = 8 packages, ~5MB, zero Qt (verified dry-run; default install
  drags 53 packages of Qt6 — always use `--no-install-recommends`). Links libx11 (client
  lib only; runs with no X server — official RPi README documents headless; people run it
  on a Pi Zero). https://github.com/supercollider/supercollider/blob/develop/README_RASPBERRY_PI.md
- **sclang not required.** supriya compiles SynthDefs natively in Python and speaks OSC to
  scsynth directly — verified locally.
- **supriya covers:** realtime server control, **nonrealtime Scores**, SynthDef building,
  patterns, tempo/meter-aware clocks. https://supriya-project.github.io/supriya/
  Caveat: essentially one maintainer, releases beta-tagged. Mitigation: the scsynth OSC
  protocol is stable and documented — worst case drive it with `python-osc` directly.
- **RT + offline both.** NRT mode (`scsynth -N`) renders an OSC score straight to WAV with
  no audio device and no JACK. Ideal here.
- **Palette fit — strongest of the FOSS engines:**
  - FM Rhodes: `\rhodey_sc` SynthDef, native port of STK Rhodey, core UGens only
    (https://sccode.org/1-522); also `MdaPiano` in sc3-plugins.
  - `sc3-plugins-server` in apt (1.8MB, verified): `JPverb`/`Greyhole` (genuinely modern
    lush reverbs), `Decimator` for bitcrush.
  - Drums: `Buffer` + `PlayBuf` one-shots, sample-accurate.
  - Sub: `SinOsc` + `tanh` waveshaping, trivial.
  - Lo-fi: modulated `DelayC` = tape wow/flutter; `Dust2`+BPF = vinyl crackle; LPF/HPF;
    saturation. All standard SC idiom.
  - Known wart: old JPverb/Greyhole crackle-after-silence issue
    (https://github.com/supercollider/sc3-plugins/issues/59) — test, or master through
    dragonfly-reverb offline.
- **CPU/RAM [inferred from Pi-class precedents]:** scsynth boots in tens of MB. Pi Zero
  runs simple patches; TidalCycles/SuperDirt runs on Pi 4s. The 6405U beats a Pi 4
  single-thread; expect dozens of rhodey-class FM voices + sampler + one reverb realtime,
  and NRT renders at multiple × realtime. No published benchmarks for this exact CPU.
- **Install:** `sudo apt install --no-install-recommends supercollider-server
  sc3-plugins-server` + `pip install supriya` in a venv. Note: `supercollider-server`
  hard-depends on `jackd` (pipewire-jack does NOT Provide it on noble — verified), so
  jackd2 gets installed; never run it. For realtime later: `apt install pipewire-jack`,
  launch via `pw-jack` (SC 3.13 includes the pipewire-JACK detection fix). For NRT none of
  this matters.

### Csound 6.18 + libcsound — runner-up
Headless CLI by design; apt minimal (7 packages, verified). Offline native; realtime works.
Built-in `fmrhode` opcode, `loscil`/`diskin2` sampling, `reverbsc` (one of the
best-sounding FOSS reverbs). Python: official `ctcsound` is stale (6.17.1, 2022; Csound 7
API break); the maintained community binding is **`libcsound` 0.13.1 (May 2026,
pure-Python wheel, Csound ≥6.18 and 7)** — verified on PyPI
(https://github.com/csound-plugins/libcsound). Csound 7 still beta — stay on 6.18. Why
second: orchestras as text strings + channel/score API = clunkier iteration than supriya's
first-class objects; modern-sounding patches more DIY.

### Faust — companion, not engine
apt has 2.70.3 (verified). Right use: author a custom tape-saturation or EP algorithm
once, then `faust2supercollider` (custom UGen) or `faust2lv2`. Compiled output targets
this CPU — no AVX issue. The JIT route into Python was DawDreamer (dead here). Optional.

### Pure Data (pd -nogui) — pass
Truly headless (`puredata-core` = 2 packages), tiny. But: patches authored in a visual
editor we don't have; generating .pd files programmatically is miserable; vanilla DSP
quality modest without externals; libpd Python glue least-maintained. Nothing beats SC here.

### Pure Python/numpy — viable fallback, real cost
Offline only, fine on this CPU (numpy wheels use runtime SIMD dispatch — verified). Drum
one-shot mixing in numpy is trivial and actually the best tool for that job. FM Rhodes = a
few hundred vectorized lines; pads via `scipy.signal.sosfilt`. Lost: the mature UGen
library — especially **reverb**, where DIY stalls; plus any free realtime path. Honorable
mention: **pippi** (2.0.0b16, Feb 2026, Cython sdist — compiles natively, AVX-safe), lo-fi
aesthetic offline composition DSP, but beta and thinly documented. Realistic estimate:
weeks to sound good vs days with SC.

### Headless LV2/CLAP hosting — one gem, otherwise a trap
- **The gem: `lv2apply` (apt `lilv-utils`) applies LV2 effects to WAV files offline, no X,
  no JACK.** With apt's `dragonfly-reverb-lv2`, `calf-plugins` (Saturator), `x42-plugins`:
  a real offline mastering chain.
- `jalv`: honest headless realtime host, but instruments need MIDI plumbing, no offline
  render. `mod-host`: GUI-less LV2 over TCP but not in Ubuntu repos, RT/JACK only. Carla:
  PyQt app, headless not first-class. Trap.
- Deeper problem: the instruments worth hosting (sfizz, Surge XT, Dexed, Vital) are **not
  in noble's repos** (verified), and third-party binaries reintroduce AVX roulette. No
  mature headless CLAP host exists. Verdict: `lv2apply` for offline FX; do not build the
  instrument platform here.

### fluidsynth — the pragmatic floor
apt 2.3.4, 4 packages minimal (verified), negligible CPU, `pyfluidsynth` 1.4.0 active (May
2026). Realtime + offline faster-than-realtime (`fluidsynth -F out.wav font.sf2 song.mid`).
Quality ceiling = the soundfont: with **jRhodes3** (multi-velocity sampled 1977 Rhodes
Mark I) the EP voice is legitimately good for this genre; GM pads weak; FX basic. Right
role: MVP keys voice and MIDI sanity-checker, not the platform.

### Everything else — verdicts
- Sonic Pi: headless officially unsupported; Erlang+Ruby+scsynth stack; wrong for 3.6GB. Skip.
- Glicol: "highly experimental," wasm-first. Skip. Cmajor: no Python story, single-vendor. Skip.
- Elementary: JS/Node. Renoise/Bitwig: no headless server mode. Reaper: batch render wants
  a display (xvfb hack), proprietary. All skip.
- **ZynAddSubFX** (apt, verified): genuine `--no-gui` with full OSC control and the famous
  PADsynth warm pads. Awkward to sequence programmatically; consider a one-off pad-stem
  renderer only.

## Offline vs realtime — offline is the smarter play

Offline-first sidesteps xruns, RT scheduling, JACK plumbing, and the muted/consumer DAC:
render with `scsynth -N`, master via `lv2apply`/sox, audition with `pw-play`. Realtime for
the record: pipewire latency = quantum/rate — noble default 1024/48000 ≈ 21.3ms; tuned
256/48000 ≈ 5.3ms (set via `pw-metadata` or `pipewire.conf.d`, monitor with `pw-top`). On
a 2-core no-AVX Pentium without an RT kernel, stable floor ≈ 512–1024 samples (10–21ms)
[inferred]. For sequenced playback none of this matters: scsynth schedules via OSC timetag
bundles, so jitter is absorbed regardless of quantum.

## Free/CC sample sources

- **Rhodes:** jRhodes3 — sf2 (https://www.audiobombs.com/items/493/jrhodes-1977-mark-i-rhodes-sound-fonts)
  and SFZ/FLAC at sfzinstruments (https://github.com/sfzinstruments/jlearman.jRhodes3d,
  https://sfzinstruments.github.io/pianos/jrhodes3c/). License: CC BY-NC samples, **CC0
  for musicians using it in music** — fine for tracks, don't resell the kit. More keys:
  https://sfzinstruments.github.io/pianos/ (SFZ needs sfizz — source build only; another
  reason to prefer sf2 via fluidsynth or plain WAV extraction into SC buffers).
- **Drums:** freesound.org CC0 filter; https://github.com/Boochi44/free-drum-samples
  (CC0); https://musical-artifacts.com/ (filterable by license/format, hip-hop sf2/sfz
  kits); Hydrogen drumkits. Royalty-free (check EULA): free-sample-packs.com lo-fi drums,
  bvker.com, 99Sounds.
- **Vinyl/tape texture:** freesound CC0 crackle, or synthesize (Dust2 + bandpass in SC —
  more controllable).

## Prior art for exactly this

Python→scsynth is a beaten trail: **renardo** (maintained FoxDot fork, ICLC 2025:
https://github.com/e-lie/renardo), **Sardine**, FoxDot, the TidalCycles/SuperDirt
ecosystem (headless on Pis). All are symbolic pattern engines firing OSC at scsynth.
supriya gives that architecture without their pattern-language opinions. Offline analogue:
**SCAMP** (0.10.0, July 2026 — composition objects rendered via fluidsynth).

## Recommended build-out

1. `sudo apt install --no-install-recommends supercollider-server sc3-plugins-server
   lilv-utils dragonfly-reverb-lv2 calf-plugins alsa-utils` (+ `pipewire-jack` when
   realtime wanted; unmute sink first).
2. `pip install supriya python-osc` in a venv (PEP 668 applies on noble).
3. Port `\rhodey_sc` into a supriya `@synthdef`; add saw-stack pad, sine-sub + tanh
   saturation, `PlayBuf` drum sampler, master-bus SynthDef (LPF → wow/flutter delay →
   saturation → Dust2 crackle → JPverb).
4. Note events → supriya NRT `Score` → WAV; master with `lv2apply` (dragonfly) if JPverb
   disappoints; audition with `pw-play`. Same SynthDefs go realtime later via `pw-jack scsynth`.
5. Keep sample buffers lean (mono 16-bit one-shots) — buffers live in scsynth RAM; budget
   ~2.5GB for everything.

**Honest tradeoffs:** supriya bus factor = 1, beta-tagged (OSC protocol is the escape
hatch); noble ships SC 3.13.0 not 3.14; JPverb/Greyhole silence-crackle edge case; nothing
here gives plugin-grade tape emulation (CHOW Tape et al.) without re-entering
binary-compatibility roulette — SC-native saturation + wow + noise gets ~90% of the
target lo-fi character (judgment, not citation).
