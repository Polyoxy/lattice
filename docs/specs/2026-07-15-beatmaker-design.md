# Lattice — Phase 1: The Beatmaker

**Date:** 2026-07-15
**Status:** Design revised after target change; awaiting user review
**Supersedes:** `2026-07-15-reharmonizer-design.md` (removed same commit; in git history)
**Research inputs:** `docs/research/brent-faiyaz-dna.md` · `docs/research/conductor-williams-dna.md` · `docs/research/audio-engine-headless.md`

---

## What changed and why

The first cut of this spec built a hymn/standards reharmonizer with Jesús Molina's
harmonic language as the target. The operator's actual target is **finished beats** —
Brent Faiyaz's dark R&B, Conductor Williams' loop craft, with Molina-grade harmony inside.
The harmony core survives unchanged (it is *more* necessary for extended neo-soul harmony,
not less). Everything around it is re-cut: the unit of output is no longer an arrangement
of a given melody but **a beat** — chords, bass, drums, texture, structure — rendered to a
WAV that knocks.

## Thesis

**Constrain generation to theory and to measured style. Delegate only taste.**

Two facts make this buildable on a Pentium:

1. Symbolic music is kilobytes. Every note-level decision — loops, voicings, basslines,
   drum patterns, micro-timing — is searchable arithmetic, not learned mush.
2. The target styles are now **measured, not vibes.** The research briefs contain 18 cited
   chord loops, documented micro-timing moves, named degrade chains, and producer-stated
   arrangement doctrine. Style is a parameter set with citations. Where a parameter is
   inferred rather than cited, the brief says so, and the engine exposes it as a dial.

One framing insight from the Conductor brief organizes the whole system: his mainstream
placements mostly sample *contemporary, analog-recorded "fake vintage" library music* —
people compose new 70s-sounding records for producers to flip; he says of the
replay-then-flip workflow, "I'm essentially making two beats." **The engine does exactly
that: it composes the record it would have sampled, then flips it like a beatmaker** —
drums under it, degrade chain over it, arrangement around it. Phase 2 adds real audio in;
the workflow is identical from the chop forward.

## What this is

`make_beat(style, key, bpm, bars, n)` → n distinct beats, each rendered to **WAV + stems +
MIDI**, each able to `explain()` every harmonic, groove, and texture decision it made.

Three style cards ship in phase 1:

| Card | The sound | What drives it |
|---|---|---|
| `FAIYAZ` | Dark R&B: minor 2–4-chord loops, close m9/maj7 stacks, half-time 65–95 BPM, composite backbeat, sub+bass-guitar, hazy texture bus | The Faiyaz brief's engine defaults (§8), all parameters cited or flagged inferred |
| `CONDUCTOR` | Loop-and-drums: soul/gospel loop treated as a "record," sparse kick+rim drums with/under it, stacked degrade chain (sampler → vinyl-sim wow/flutter + pump → tape), drumless "score mode" | The Conductor brief's cheat-sheet (§10) |
| `MOLINA` | Gospel/jazz harmonic density: the phase-1-v1 reharmonization machinery as a style — subdivided harmonic rhythm, secondary dominants, passing diminished, gospel voicings, V7♭9♭13 kickers | The v1 substitution catalog, reweighted |

Cards are parameter sets, not code paths — every dial (loop grammar weights, swing band,
micro-offsets, degrade depth) is user-overridable per call.

## Non-goals for phase 1

- **No real-audio sampling or chopping.** The chop engine over user-supplied WAVs is
  phase 2. Phase 1 synthesizes its own source material.
- **No vocals.** Melody/topline generation is out; texture beds are instrumental.
- No learned model — scorers are hand-coded from the briefs; phase 3 learns taste.
- No realtime audio, no MIDI input, no web UI, no LLM. Later phases.
- No custom DSL grammar. The Python API is the DSL.
- **No cloning of identity.** We model the *language* (public, documented technique and
  theory), not the recordings: no samples of the reference artists' records, no
  reproduction of Conductor's actual tag (a user-supplied tag WAV can be overlaid
  generically). Output is original material in a style.

## Constraints

| | |
|---|---|
| Host | lexy — Ubuntu Server 24.04, headless, no GUI |
| CPU | Pentium 6405U, 2c/4t. **No AVX/AVX2/FMA** (verified) — pip binary DSP wheels SIGILL; pedalboard and DawDreamer confirmed dead. apt-compiled engines only. |
| RAM | 3.6GB total, ~2.5GB available. Sample buffers stay lean (mono 16-bit one-shots). |
| Audio | pipewire + ALSA, sink currently muted (`wpctl set-mute @DEFAULT_AUDIO_SINK@ 0`) |
| Operator | Strong programmer, not a keyboard player — `explain()` is a core deliverable, the interface by which output is judged and the ear gets built |

Rendering is **offline (NRT)**: no xruns, no JACK plumbing, no RT tuning, renders faster
than realtime. The identical SynthDefs go realtime in a later phase when a keyboard exists.

---

## Architecture

```
        StyleCard (FAIYAZ | CONDUCTOR | MOLINA) + user dials + seed
              │
              ▼
  ┌─ harmony engine ────────┐  theory core: line-of-fifths spelling (unchanged from v1)
  │  loop grammar → lattice │  2–4 chord loop candidates → elaboration lattice
  │  → beam search → loop   │  (kickers, passing chords, harmonic-rhythm subdivision)
  └─────────────────────────┘
              │  spelled chord loop
              ▼
  ┌─ voicing engine ────────┐  close stacks / gospel templates, register policy,
  │  exact Viterbi DP       │  roots delegated to bass, LIL table, top-voice smoothness
  └─────────────────────────┘
              │  voiced keys part
              ▼
  ┌─ groove engine ─────────┐  drums (pattern grammar per card), bass (sub + lick
  │  events on a tick grid  │  grammar), keys rhythm; then the pocket pass:
  │  + pocket pass          │  micro-offsets, velocity fields, swing, humanize
  └─────────────────────────┘
              │  Part[] of Event(tick, micro_ms, dur, vel)
              ▼
  ┌─ arrangement ───────────┐  loop → 1:30–2:30 timeline: layer mutes, drum dropouts,
  └─────────────────────────┘  filter moves, half-time drop, transpose event, bookends
              │  Timeline
              ▼
  ┌─ render ────────────────┐  supriya SynthDefs → scsynth NRT → per-part stems
  │  scsynth -N (offline)   │  → texture/degrade bus per card → master (lv2apply)
  └─────────────────────────┘
              ├──► beat.wav + stems/*.wav
              ├──► beat.mid (per-part tracks)
              └──► explain() — every decision, named and justified
```

Every stage is independently testable: the harmony engine emits spelled chords, the
groove engine emits events, the renderer consumes a Timeline. A stage can be swapped
(phase 2 replaces "synthesize source" with "chop user audio") without touching neighbors.

---

## Core data model

### Theory core — unchanged from v1, and load-bearing

Pitch is an integer on the **line of fifths** (`tpc`), never a MIDI number. C♯ (7) and
D♭ (−5) are different objects; intervals are tpc arithmetic; MIDI is a one-way projection
computed at the boundary. This is what lets the engine tell a ♯9 from a ♭3, spell
G7♭13 correctly, and voice Em6add9 as the tab says rather than as an integer soup.
The neo-soul palette (m9, 6add9, maj7♯11, 7♭13, aug) exercises spelling *harder* than
hymn harmony does.

```
pitch_class = (tpc * 7) mod 12       letter = "CDEFGAB"[(tpc * 4) mod 7]
alteration  = floor((tpc + 1) / 7)   midi   = 12*(octave+1) + LETTER_SEMITONES[letter] + alteration
```

`Chord = (root: Tpc, intervals: frozenset[FifthInterval], bass: Tpc | None)` — identity is
the spelled interval set; symbols are renderings.

### New types

| Type | Purpose |
|---|---|
| `Event` | `(tick, micro_ms, dur_ticks, velocity, pitch \| sample_id)` — grid position and pocket offset are **separate fields**; the groove *is* that separation |
| `Part` | ordered events + role (`KEYS, BASS, SUB, KICK, SNARE, HAT, PERC, TEXTURE`) |
| `Loop` | spelled chord loop + per-slot durations (harmonic rhythm) |
| `Timeline` | sections over a Loop: mute masks, filter/transpose/dropout events |
| `StyleCard` | frozen dataclass of every dial: loop grammar weights, groove params, palette, degrade chain, arrangement policy — each field annotated `cited` or `inferred` |
| `Beat` | Loop + Parts + Timeline + card + seed; knows `render() / stems() / to_midi() / play() / explain()` |

Grid: 960 ticks/quarter. Swing and pocket are *functions writing `micro_ms`*, never grid
mutations — quantize-independence is what keeps MIDI export clean and tests deterministic.
All generation is seeded; same seed, same beat, bit-for-bit.

---

## Harmony engine

### Loop grammar (FAIYAZ card values, all cited in the brief)

- Center: weighted minor keys {Am, Bm, C♯m, Dm, Fm, Gm, G♯m}; Aeolian home.
- Loop of 2–4 chords drawn from functions {i7/i9, v7, ♭VImaj7, iv7/iv6add9, ♭III},
  favoring documented shapes: ♭VI→i (Trust), i→v (Rehab), iv–v–i–♭VI (Rolling Stone),
  i–♭VI–iv (Show U Off), tonic-avoiding loops (Dead Man Walking, Loose Change) allowed.
- Colors, probability-weighted: Dorian natural-ii swap (p≈0.3), ♭II/half-step vamp
  (All Mine/Price of Fame device), harmonic-minor **V7(♭9/♭13) kicker** closing the loop
  (p≈0.25, the Poison/Talk 2 U move).
- Extensions are the *default*: sevenths always, ninths common, 6add9 on tonic.
- **Verse = chorus.** One loop per beat. The only modulation is a whole-loop transpose
  event (±3–5 semitones) placed by the arranger — the documented "fake I–V" trick.
- **Style-off switches matter as much as style-on:** no tritone subs, no chromatic
  mediants in the FAIYAZ card — their absence is documented. The v1 catalog still
  implements them; the MOLINA card turns them on.

### Elaboration lattice (the v1 machinery, retargeted)

The loop is laid on a slot grid (8th-note default). Candidates per slot: the loop chord
(hold), or an elaboration — secondary dominant, passing diminished, backdoor ii–V,
related-ii insertion, kicker alterations — from the v1 substitution catalog, weighted by
card. Beam search (width 100, diversity-enforced: dedupe by root-motion signature, ≥3-slot
difference) scores paths on voice-leading cost, tension arc, functional coherence,
harmonic-rhythm prior, and idiom bonus. For the FAIYAZ card elaboration is sparse
(harmonic rhythm stays 1–2 chords/bar); for MOLINA it subdivides hard — that dial *is* the
difference between the cards at the harmony layer.

**The avoid-note rule survives as a voicing filter:** no voice may form a minor 9th
against another chord tone except above a dominant's root. Pruned, not penalized — every
expressible voicing is playable, no tuning weight can let mud through.

### Voicing

Exact Viterbi DP over templates (cost is Markovian — adjacent-pair voice-leading motion).
FAIYAZ templates: close-position 4–5 note stacks (the "2-3-2 / 3-2-3" shapes), mid
register C3–C5, **rootless when the bass part holds the root** (register delegation is a
hard rule, not a preference), deliberate gaps — density ceiling per card. MOLINA adds
gospel templates from v1: drop-2, quartal, upper-structure triads, 4–3 suspensions.
Low-interval-limit table enforced everywhere. Top voice moves by step where possible —
smoothness term in the DP.

## Groove engine

Patterns are generated from per-card grammars, then the **pocket pass** writes micro-timing
and velocity. All figures below ship as defaults with the brief's confidence flag attached.

**FAIYAZ drums (cited):** felt 65–95 BPM half-time (grid at felt tempo, backbeat on 3);
sparse kick (1–3 hits/bar, never four-on-floor); backbeat = **layered composite** — rim +
snap + clap as separate simultaneous events with distinct samples, **snap rushed −10..−20
ms, clap dragged +10..+20 ms**; hats two-step with alternating velocities, occasional
1/16 rolls; low-velocity hand-perc bed filling pockets; **tom/bongo turnaround in the last
half-bar of each 4/8-bar phrase**; two alternating pattern variants (A flowing, B choppy)
swapped by the arranger. Swing on off-8ths/16ths from a tunable band, default 54–62%
(**inferred** — no cited percentage exists; it's a dial). Humanize: ±1σ timing jitter
~4 ms, velocity jitter ~8%, both seeded.

**CONDUCTOR drums (cited):** 80–100 BPM; kick + rim/snare "1-2" skeleton, ghost kicks for
thickness, one ride/hat placed "in a space" per phrase; drums mixed *with/under* the keys
bus, dry and mid-forward, sub emphasis absent by default (single "big bass note" event
allowed per section, p small); **drumless "score mode" with p≈0.15** — the beat is the
loop and texture alone; no fixed swing — performance jitter only (his groove is inherited
from breaks and hands, not a swing knob).

**Bass (cited):** two coupled parts. `SUB` — sine, straight roots, long notes, mono.
`BASS` — bass-guitar-voiced line: root anchors plus a lick grammar (approach notes into
downbeats, call-and-response fills in bar 2/4, walk-downs at turnarounds, R&B double-stab),
occasional glide (portamento event, p small), saturation at render. Sidechain duck to kick,
4–5 dB, at render. MOLINA card may let bass reharmonize (the bassline-reharm move);
FAIYAZ/CONDUCTOR keep bass consonant with the loop.

**Keys rhythm:** FAIYAZ — sustained stabs on chord changes plus anticipations (push by an
8th, p≈0.3), gaps honored; CONDUCTOR — the loop plays as if sampled: chord-block hits on a
chop-like grid with occasional re-attack jitter; MOLINA — comping density dial up,
passing-chord hits on subdivided slots.

## Arrangement

Timeline over the loop, 1:30–2:30 (both briefs agree on short): intro (texture/keys only,
1–2 loop cycles) → sections differentiated **only** by layer mutes, drum dropouts
("quick tension, quick release" — drop hats a bar), filter moves (LPF sweep = the "phone
effect"/muffle), half-time drop, optional whole-loop transpose event near the outro
(+3 st, the documented device) → outro (strip back to texture). One-pass doctrine: the
arranger commits; no post-hoc micro-editing pass exists to fake "polish" the references
deliberately avoid. Optional user-supplied tag WAV overlaid at section boundaries
(mixtape framing — generic mechanism, no shipped tag).

## Render

**Engine: scsynth NRT via supriya** (apt `supercollider-server sc3-plugins-server`
`--no-install-recommends`; pip `supriya` — pure-Python wheel, verified importable on this
box; OSC protocol is the escape hatch if supriya's solo-maintainer risk bites).

**SynthDefs (phase 1 palette):**
- `rhodey` — port of the STK-derived `\rhodey_sc` FM electric piano (core UGens only);
  fallback voice: fluidsynth + jRhodes3 soundfont (sampled '77 Mark I) for A/B and MIDI
  sanity.
- `pad` — detuned saw stack → LPF → slow envelope (strings-as-cake stand-in; real string
  articulations are a later-phase luxury).
- `sub` — sine + `tanh` saturation; `bassgtr` — filtered saw/square hybrid + pluck env +
  drive (Rickenbacker-ish attitude, not emulation).
- `drum` — `PlayBuf` one-shots from CC0/free kits (freesound CC0, Boochi44 pack,
  musical-artifacts; licenses recorded in an asset manifest; `lattice fetch-assets`
  downloads and verifies).
- Texture generators: vinyl crackle = `Dust2`→BPF bed; cassette hiss = filtered noise at
  −40ish dB ("you just feel them").

**Per-card bus chains (the identity layer):**
- FAIYAZ master feel: keys/pads ducked by kick (Compander, 4–5 dB); plate-style JPverb
  ~2.5 s on filtered sends (HP+LP on the return — the Abbey Road trick); filtered
  low-feedback delay into the reverb; tape-ish `tanh` stage; **brick-wall LPF ~15–16 kHz
  on the mix**; crackle bed under everything; bass strictly mono.
- CONDUCTOR degrade stack, in series (order is the sound): sampler color (mild bit/rate
  reduction — `Decimator`) → **vinyl-sim wow/flutter** (modulated `DelayC`, slow drift +
  faster flutter) **+ program-pump compression** (slow-release Compander over the whole
  bus — the SP "ducking glue") → tape stage (soft `tanh`, slight HF loss) → matte master.
  Keep artifacts; no de-clicking.
- MOLINA: cleaner — room reverb, light tape, no wow.

**Master:** offline `lv2apply` chain (dragonfly-reverb if JPverb's silence-crackle wart
bites, calf saturator, x42 limiter) → `sox` trim/fade/dither → 44.1 kHz 16-bit WAV.
Stems render as solo NRT passes (cheap — NRT is faster than realtime). Audition:
`beat.play()` → `pw-play` (unmute sink first).

## Output and explain()

`out/<slug>/beat.wav`, `stems/{keys,bass,drums,texture}.wav`, `beat.mid` (per-part
tracks, micro-offsets baked into absolute ticks), `beat.json` (full parameter dump —
seed, card, dials — sufficient to regenerate bit-identically), and `explain()`:

> **Loop** — C♯ Aeolian, 4 bars: C♯m9 (i9) → Amaj7 (♭VImaj7) → F♯m7 (iv7) → G♯m7 (v7).
> The v stays minor — dominant function without a leading tone (the Rehab move). Voicings
> close-position, rootless above the sub, top voice steps E→E→F♯→D♯.
> **Groove** — 72 felt half-time; snap −14 ms, clap +11 ms on the 3; hats 2-step
> velocities 96/64, swing 57%; bongo turnaround bar 4.
> **Texture** — FAIYAZ bus: kick-duck 4.3 dB on keys; plate 2.4 s filtered 400 Hz–9 kHz;
> mix LPF 15.5 kHz; crackle −38 dB.

For a non-playing operator this is the primary interface, and it doubles as the log the
taste model trains against in phase 3.

## The API

```python
from lattice import make_beat, StyleCard

beats = make_beat(style="faiyaz", key="C#m", bpm=72, bars=4, n=5, seed=7)
b = beats[0]
b.explain()
b.render("out/night-drive/")      # WAV + stems + json
b.to_midi("out/night-drive/beat.mid")
b.play()

card = StyleCard.faiyaz(swing=0.60, drumless=False, lpf_hz=14500)   # every dial overridable
make_beat(style=card, key="Gm", bpm=88, bars=8, n=3, seed=11)
```

---

## Testing

### Unit
Theory core (line-of-fifths algebra, MIDI projection incl. C♭/B♯ octave boundary, chord
identity, enharmonic equivalence), every substitution rule, tick↔ms math, pattern
grammars, seeded determinism (same seed ⇒ identical `beat.json`).

### Property-based (hypothesis)
For any generated beat, any card, any seed: no minor-9th voicing violation outside the
dominant-root exception; no low-interval-limit violation; voicing spans within hand
policy; backbeat present when drums enabled; micro-offsets within card bounds; sub part
strictly root-consonant; bass mono at render config; MIDI round-trips losslessly.

### Calibration — the honest metric, now against the actual corpus
The research gives a **reference set with citations**:

1. **Harmony coverage** — the documented loops must be *expressible*. Reference set =
   17 tracks: Trust, Dead Man Walking, Rehab, Wasting Time, Poison, Clouded, All Mine,
   Gravity, Rolling Stone, Talk 2 U, Stay Down, Show U Off, Been Away, Make It Out,
   Price of Fame, Loose Change, Upset Feet. (Jackie Brown is carried as unresolved —
   detectors disagree on its loop — and excluded until settled.) Each must be reachable
   in the FAIYAZ loop grammar or flagged as a deliberate exclusion. Target ≥90%.
2. **Harmony calibration** — score each documented loop within the generator's candidate
   space for its key/tempo; each must rank in the top 5% of scored candidates. A
   documented loop the scorer dislikes = a taste bug with a number attached.
3. **Groove calibration** — distributions of generated micro-offsets, velocities, and
   densities fall inside the documented bands (snap −10..−20 ms, clap +10..+20 ms, kick
   sparsity, hat alternation ratio). Tested statistically over 100 seeded beats/card.
4. **Render sanity** — golden-file spectral checks: mix LPF ceiling present (FAIYAZ),
   crackle floor present, wow/flutter modulation measurable on CONDUCTOR renders,
   drums-vs-keys RMS ratio in the "with/under" band; render is deterministic per seed.

### The ear test
Criteria 1–4 can pass while the output is dead. The deciding test stays human: render
three beats per card, listen on the Beats, and answer one question per card — *would a
producer keep this loop?* FAIYAZ: does it haze? CONDUCTOR: does it knock *and* sound like
a found record? MOLINA: does the harmony surprise without breaking?

## Dependencies

| Layer | Packages |
|---|---|
| Python (pip, venv) | `supriya`, `python-osc`, `mido`, `numpy` (+ dev: `pytest`, `hypothesis`, `ruff`, `mypy` strict) |
| System (apt, `--no-install-recommends`) | `supercollider-server`, `sc3-plugins-server`, `lilv-utils`, `dragonfly-reverb-lv2`, `calf-plugins`, `x42-plugins`, `fluidsynth`, `sox`, `alsa-utils` |
| Assets (`lattice fetch-assets`) | jRhodes3 sf2; CC0 drum kits (freesound/Boochi44/musical-artifacts); licenses recorded in `assets/MANIFEST.md` |

**Hard rule from verified research: no pip packages that ship compiled DSP** (no AVX on
this CPU — pedalboard/DawDreamer/signalflow are dead here). numpy is safe (runtime SIMD
dispatch, verified). apt binaries are safe (amd64 baseline).

## Risks

| Risk | Mitigation |
|---|---|
| **The sound ceiling.** SynthDef craft decides whether renders feel like records or like a demo scene. This is now the project's central risk — bigger than harmony. | The degrade chains are the great equalizer: both reference styles *bury* raw timbre under texture (that's the aesthetic, documented). jRhodes3 fallback for keys A/B. lv2 master chain as a second opinion. Iterate by ear against reference tracks; budget real time for it. |
| **Groove authenticity without a learned model.** Hand-coded humanization can feel mechanical. | Parameters are measured, not guessed (rush/drag values, velocity alternation are cited); calibration bands make drift detectable; swing stays a dial; phase 3 learns the residual. |
| **Inferred parameters wearing cited costumes.** | Every StyleCard field carries its confidence flag from the briefs; `explain()` surfaces them; inferred defaults are dials, not constants. |
| **supriya bus factor = 1, beta-tagged.** | scsynth's OSC protocol is stable and documented; worst case we emit OSC score files directly with `python-osc`. NRT score format is plain data. |
| **Scope creep toward the chop engine.** | Hard phase boundary: phase 1 never reads audio in, only out. The Timeline/Part interfaces are chop-ready by design. |
| **RAM.** | scsynth boots in tens of MB; NRT streams to disk; kits are mono 16-bit; budget enforced by keeping buffers under ~200 MB. |

## Acceptance criteria

1. All property-based invariants hold across cards and seeds.
2. Harmony coverage ≥90% of the documented-loop reference set; every covered loop ranks
   top-5% in its candidate space.
3. Groove distributions inside documented bands over 100 seeded beats per card.
4. `explain()` names loop functions, pocket offsets, and texture chain correctly for
   every beat (spot-checked against `beat.json`).
5. Full pipeline — grammar to mastered WAV, 2:00 beat — completes in ≤5 minutes wall
   clock on lexy; regeneration from `beat.json` is bit-identical.
6. **The ear test: three beats per card on the Beats. At least the FAIYAZ card produces
   one beat you'd play twice voluntarily.** If nothing clears that bar, we stop and fix
   before any phase 2 work.

## Roadmap

| Phase | | |
|---|---|---|
| **1** | **The Beatmaker** | This spec. Synthesized source, three style cards, WAV/stems/MIDI out, explain(). |
| 2 | The Chop Engine | Real audio in: user-supplied samples/packs; pad-to-pad chop grammar, boundary-agnostic splices, tempo-nudge; the CONDUCTOR card gains its true workflow. |
| 3 | Taste | Learned ranker over loops/grooves replacing the idiom term; trains on explain()/beat.json logs + curated corpus. |
| 4 | The Console | Web UI over Tailscale (TS/Next): variant browser, dials, waveform/piano-roll, render queue. |
| 5 | Intent | Local LLM: "darker, more space on the turnaround" → card dial deltas. |
| 6 | The Partner + Improvisation | Realtime scsynth (same SynthDefs, `pw-jack`), MIDI keyboard in; neural generation for runs/fills — the one layer where search is the wrong tool. |

## On "exact … and better"

"Exact" is delivered as measured parameters with citations — the engine's FAIYAZ card
rushes the snap and drags the clap because sources document the move, not because it
sounds plausible. "Better" is delivered the only honest way: coverage (every loop the
grammar admits, scored), explanation (every choice named), speed (five beats in minutes),
and novelty search (style-valid loops rare in the corpus — the road past imitation). The
engine proposes; you dispose.
