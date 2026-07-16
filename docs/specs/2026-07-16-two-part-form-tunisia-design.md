# Lattice — Two-Part Form + the TUNISIA Card

**Date:** 2026-07-16
**Status:** Design approved, ready for planning
**Scope:** One engine capability (two-part song form) + one style card (TUNISIA) + one produced single. All at the symbolic/preview layer; full-production rendering is the parked render-stack plan.

---

## What this is

Two things that ship together because the second needs the first:

1. **Two-part form** — a beat can hold two contrasting loops (an *A* vamp and a *B* bridge) sharing key and tempo. The arranger already emits `intro → a → b → drop → a → outro`; today every section plays the same loop. This makes A-sections play the vamp and B-sections play the bridge, with a voice-leading-aware handoff across the seam.

2. **The TUNISIA card** — a style tuned to the harmonic language of Latin-jazz: a D-minor home, the ♭II→i half-step "Spanish tinge" as the A-vamp, a swinging ii–V–i as the B-bridge, faster bebop-leaning tempo, altered-dominant spice, grand-piano-plus-upright voice.

The deliverable that proves both is **one original single** composed with the card and released at preview quality.

## What this is NOT

- **Not a cover, not a transcription.** No existing tune's melody or specific chart is reproduced. The card generates original loops from a grammar, exactly as the other cards do. The harmonic *devices* it favors (a dominant a half-step above a minor tonic, Phrygian-dominant color, ii–V–i) are general jazz-harmony vocabulary, free to anyone; the output is wholly original.
- **Not new harmony machinery.** TUNISIA reuses the existing line-of-fifths core, substitution catalog, voicing DP, groove engine, and arranger. It is a parameter set plus a bridge-grammar bias.
- **Not the render stack.** Output is MIDI + `beat.json` + `explain()` + the fluidsynth grand-piano preview. Full production waits for the parked render-stack plan; this single re-renders through it later.
- **No melody-input / lead-sheet path.** That remains a future phase.

## Constraints

| | |
|---|---|
| Branch | new `two-part-form` off `main`; render-stack branch stays parked |
| Reuse | grammar, score, substitutions, voicing, groove, pocket, arrange, beat, midi, explain, api — extend, don't fork |
| Determinism | same seed ⇒ bit-identical `beat.json`, unchanged for existing single-loop beats |
| Compatibility | existing cards (faiyaz/conductor/molina) and their released `beat.json` files keep producing byte-identical output — two-part form is opt-in per card |
| Tooling | Python 3.12, uv, mypy --strict, ruff (E501 on), pytest + hypothesis, no comments, plain commits |
| Quality | the calibration/property suites stay green; new behavior gets its own tests |

---

## Architecture

The change is threaded through five existing layers. Each extension is additive and gated so single-loop cards are untouched.

```
  StyleCard  + bridge fields (has_bridge, bridge_function_pool, bridge weights…)
       │
       ▼
  grammar     the A loop as today; NEW: a bridge loop drawn from the bridge pool,
              scored to CONTRAST the A loop (different root motion, cadential)
       │
       ▼
  elaborate + voicing + groove   run TWICE — once per loop — producing an
              A rendering and a B rendering; the B voicing DP is SEEDED from
              the A loop's last voicing so the seam voice-leads
       │
       ▼
  Beat        + section_b: SectionRender | None  (the B loop's loop/segments/
              voicings/parts). parts_a/parts_b stay the A loop's drum variants.
       │
       ▼
  arrange     unchanged section list; NEW: unrolled() routes "b"/"drop-after-b"
              cycles to the B rendering when section_b is present
       │
       ▼
  MIDI / explain / preview   B loop's parts render in the b cycles; explain()
              prints both loops labelled A / B
```

### The `SectionRender` unit

To avoid a tangle of parallel fields, the per-loop rendering is bundled:

```python
@dataclass(frozen=True, slots=True)
class SectionRender:
    loop: Loop
    segments: tuple[Segment, ...]
    voicings: tuple[tuple[SpelledPitch, ...], ...]
    parts_a: dict[Role, tuple[Event, ...]]   # drum variant A + bass + keys for THIS loop
    parts_b: dict[Role, tuple[Event, ...]]   # drum variant B + bass + keys for THIS loop
```

`Beat` gains `section_b: SectionRender | None`. The existing top-level `loop`, `segments`, `voicings`, `parts_a`, `parts_b` remain the **A** rendering (backward compatible — no field renames, existing beats set `section_b=None`). This keeps every current `beat.json` byte-identical: the JSON gains a `section_b` key that is `null` for single-loop beats, and the `to_json` determinism tests extend to cover the populated case.

### unrolled() with a bridge

`Beat.unrolled()` currently walks the timeline, choosing `parts_b` (drum variant B of the single loop) for `kind == "b"` sections and `parts_a` otherwise. This is unchanged for single-loop cards (`section_b is None`).

When `section_b` is present, the a-vs-b drum-variant distinction is *replaced* by the a-loop-vs-b-loop distinction — the contrast now comes from harmony, not just drums:

- `kind == "b"` → the bridge: `section_b.parts_a`.
- `kind in {"a", "intro", "outro"}` → the A rendering: `parts_a` (intro/outro muted per the section).
- `kind == "drop"` → the A rendering, `parts_a`, muted per the drop. A drop is a brief mostly-muted tension-release returning toward home; it always uses the A texture regardless of what preceded it (no drop-origin tagging needed).
- The transpose lift applies uniformly — both loops shift together, a lift is global.

`SectionRender` carries both drum variants (`parts_a`, `parts_b`) for type uniformity with the A rendering; the bridge uses `parts_a` only, and `section_b.parts_b` is computed but unused in phase 1 (a future refinement could alternate bridge drum variants across multiple `b` sections). The A rendering continues to use both variants only when `section_b is None`.

### The seam (the musical point)

Two mechanisms keep the A→B→A transitions from lurching:

1. **Bridge voicing continuity.** `realize()` gains an optional `seed_from: Stack | None` — the bridge's voicing DP starts its first-candidate search biased toward minimal motion from the A loop's *last* voicing, so the top voice steps across the boundary instead of leaping.
2. **Contrast scoring.** The bridge loop is chosen not just for idiom fit but to *differ* from the A loop: a `contrast(a_loop, b_loop)` term rewards different root-motion signature and a cadential shape (ends on a dominant→tonic pull back into A). This is what makes B feel like a bridge, not a second verse.

---

## The TUNISIA card

A new `StyleCard` plus the bridge fields. Values are musically reasoned (this is a new style, so they are *designed*, not corpus-cited — provenance marks them `designed`).

**A-vamp grammar (the Spanish tinge):**
- Center: weighted toward `Dm`, plus `Am`, `Em`, `Gm`, `Cm` — natural-minor homes.
- A-loop favors the **♭II→i** half-step move: pool centered on `{i7, i9, i6add9, bII, bII7, v7, iv7, bVImaj7}`, with the ♭II (as a maj7 *or* a dominant ♭II7 — the tritone-sub-of-V "Spanish" color) weighted high. This activates the dormant `p_phrygian_vamp` dial as a real probability (default 0.6 for TUNISIA).
- Short loops favored (2 chords — the vamp is hypnotic): `loop_len_weights` weighted to length 2.

**B-bridge grammar (the swing):**
- `has_bridge = True`; `bridge_function_pool` = a ii–V–i / turnaround vocabulary: `{iim7b5, V7b9, i7, iv7, bVII7, V7b13, ii7, v7}`, favoring 3–4 chord cadential loops that resolve back toward the tonic. This is where the secondary dominants and the (already-implemented) tritone subs earn their keep.
- `bridge_len_weights` weighted to lengths 3–4.

**Feel:**
- `bpm_range = (128, 152)` felt — bebop-leaning, rendered half-time-aware like the other cards (the pocket layer already swings). Actually swung: `swing_band = (0.58, 0.66)`.
- `elaboration_density` moderate (0.4) — busier than faiyaz, less wall-of-chords than molina; `max_changes_per_bar = 3`.
- `allow_tritone_sub = True`, `allow_chromatic_mediant = False` (Spanish tinge is diatonic-plus-♭II, not mediant-drifty).
- Voicing: rootless, `voicing_density` 0.7 (fuller than faiyaz, leaner than molina), register 43–79, molina's six templates plus `add9`.
- Drums: a light latin-jazz kit — brushed/ride-forward is out of scope for the symbolic layer, but the groove favors `ride`/`bongo`/`shaker` in the perc bed and a lighter kick. `p_drumless` low (0.1) — this tune wants motion. Groove params: `p_perc_bed` high (0.7) for the Latin percussion feel, `ghost_kicks` off, `p_hat_roll` low.
- Preview program: grand piano + upright (reuse molina's GM program map by adding `"tunisia"` to `_CARD_PROGRAMS`).
- Texture (render-plan values, consumed later by the render stack): clean-ish room like molina but a touch of tape warmth — `lpf 17000, crackle -55, wow 0.05, pump 1.5, reverb 1.6, tape 0.25`.

---

## Data flow for `make_beat` with a bridge card

```
make_beat(style="tunisia", key=None, bpm=None, bars, n, seed)
  per beat i:
    rng, key, bpm, A-length  ← as today
    A_loop   = ranked A candidates[i % …]
    A_render = elaborate → realize → groove (drum A/B + bass + keys)   # SectionRender
    if card.has_bridge:
        B-length ← draw from bridge_len_weights
        B_loop   = best bridge candidate by (idiom fit + contrast(A_loop, B_loop))
        B_render = elaborate → realize(seed_from=A_render last voicing) → groove
        section_b = B_render
    else:
        section_b = None
    timeline = build_timeline(...)              # ensures ≥1 'b' section when has_bridge
    Beat(..., section_b=section_b)
```

The bridge draws from the **same per-beat rng stream**, at a fixed position (after the A rendering, before the timeline) so determinism holds and adding a bridge to a card never perturbs a single-loop card's stream.

`build_timeline` gains one guarantee: when `has_bridge`, the section list contains at least one `b` section (today it usually does, but a very short target could omit it — the builder forces one).

---

## Testing

**Unit / property (fast):**
- `SectionRender` and `Beat.section_b` round-trip through `to_json` deterministically; single-loop beats serialize `section_b: null` and stay byte-identical to pre-change output (golden check against a committed fixture for faiyaz seed 7).
- `contrast(a, b)` is higher for genuinely different loops than near-identical ones.
- `realize(seed_from=…)` produces a first voicing whose top voice is within a small step of the seed's top (seam continuity), and without `seed_from` behaves exactly as before (existing voicing tests unchanged).
- With a bridge card, `unrolled()` plays bridge parts during `b` cycles and A parts during `a` cycles — asserted by checking which loop's pitches appear in which cycle's events.
- Property sweep extended: TUNISIA added to the three-card invariant test (voicing constraints, per-bar cap, sub-root lock, determinism) across seeds.
- The existing calibration suite is untouched (TUNISIA is not in the Faiyaz corpus; its A-pool must still pass `expressible` for its own documented shapes — a small TUNISIA-shape reachability test, not a percentile gate).

**Character (the ear, slow-marked where it renders):**
- TUNISIA beats reach the ♭II→i move in the A loop across seeds (the Spanish tinge is actually present, not just possible).
- Bridge loops differ from their A loop (root-motion signature differs) in ≥90% of seeds.
- Generated preview MIDI has both loops' harmony in the right sections.

**The deciding test (human):** render three TUNISIA candidates to the grand-piano preview; the vamp should hypnotize and the bridge should *lift and return*. If no candidate does both, the card's grammar/weights are wrong and get retuned — not the test.

## Acceptance criteria

1. All existing tests stay green; existing cards' `beat.json` output is byte-identical (golden fixture proves it).
2. Property invariants hold for TUNISIA across seeds.
3. A TUNISIA beat with a bridge: `explain()` prints both loops labelled A and B; `unrolled()` routes them to the right sections; `beat.json` round-trips deterministically with a populated `section_b`.
4. The Spanish-tinge (♭II→i) appears in TUNISIA A-loops and bridges genuinely contrast — measured over seeds.
5. **One original single**, composed with TUNISIA, where the vamp hypnotizes and the bridge lifts — the human ear test — saved with its `beat.json` and released at preview quality.

## Risks

| Risk | Mitigation |
|---|---|
| **`Beat` field sprawl / backward-compat break.** | `SectionRender` bundles the per-loop fields; `section_b` is additive and defaults `None`; a golden `beat.json` fixture for an existing card is the regression tripwire. |
| **The bridge feels like a second verse, not a bridge.** | `contrast()` scoring + cadential bridge pool + the seam voice-leading; the ear test is the final judge. |
| **Determinism drift** — adding the bridge draw perturbs rng for single-loop cards. | Bridge draw is gated on `has_bridge` and positioned after the A rendering; single-loop cards never enter that branch, so their stream is provably unchanged (golden fixture confirms). |
| **TUNISIA is a designed card, not corpus-calibrated** — could sound generic. | Provenance honestly marks it `designed`; the ear test gates release; a future corpus pass can calibrate it like faiyaz. |
| **Latin percussion realism** at the symbolic/GM layer is limited. | Accept for preview; the render stack's real kit + texture is where the Latin feel lands. Groove favors the right perc sounds now. |

## Roadmap fit

This slots between the two phase-1 plans. It does not block the render stack (parked, resumes after) and the render stack consumes `Beat.unrolled()` — which already accounts for `section_b`, so the bridge audio comes for free once rendering lands. The single releases at preview quality now and becomes the render stack's first full-production track later.
