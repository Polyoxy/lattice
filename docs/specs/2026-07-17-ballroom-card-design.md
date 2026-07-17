# Ballroom Card — Design

1930s ballroom orchestra as a style card: stride-flavored grand piano out front,
upright bass walking underneath, brushes, and a string section sustaining behind.
Foxtrot tempo band, AABA form, major keys. Research grounding in
`docs/research/ballroom-dna.md`; every parameter below carries a provenance label
(cited / inferred / designed) and the brief holds the sources.

Decisions locked with the user: the sound is the full ballroom (piano + bass +
brushes + strings), medium foxtrot 104–126 bpm, strings as sustained velvet (no
countermelodies), GM voices now with a sampled-voice upgrade path later. Elegant,
not lo-fi: no crackle, no tape wobble.

## 1. The card

New `BALLROOM: Final = StyleCard(...)` in `cards.py`, registered in `get_card`.
Major-key only.

| Field | Value | Provenance |
|---|---|---|
| `name` | `"ballroom"` | — |
| `centers` | unused minor list kept minimal `("Dm",)` | designed (never selected) |
| `p_major_center` | `1.0` | designed — the era's dance book is major |
| `major_centers` | `("F", "Ab", "Eb", "C")` | inferred — band keys of the period book |
| `bpm_range` | `(104, 126)` | cited — ISTD slow foxtrot 112–120 sits inside; brief §7 |
| `loop_len_weights` | `((2, 0.35), (4, 0.65))` | designed — AABA phrases breathe in 2s and 4s |
| `has_bridge` | `True` | cited — 32-bar AABA dominance, brief §6 |
| `section_pattern` | `"AABA"` (new field, default `"AB"`) | cited — the era's native form |
| `p_transpose_event` | `0.0` | designed — dance floors don't modulate mid-tune |
| `target_len_s` | `(150, 210)` | designed |

`section_pattern` is a new `StyleCard` field consumed by `arrange.py`: the
existing A/B alternation becomes the `"AB"` default, and `"AABA"` plays the vamp
twice before each bridge. Single-loop cards ignore it. The golden fixture
(`tests/fixtures/faiyaz_seed7.mid`) and tunisia's released beat.json must stay
byte-identical — the field only changes behavior when set.

## 2. Harmony vocabulary

Two new chord qualities in `theory/chord.py` `QUALITY_IVS` (the rest already
exist — `9`, `dim7`, `6add9`, `m6add9`):

```python
"6": (iv.M3, iv.P5, iv.M6),
"m6": (iv.m3, iv.P5, iv.M6),
```

The added-sixth tonic is the card's signature sonority — cited (Martin 2023,
MTO: jazz's tonic of choice by the early 1930s; brief §6). Tonic maj7 is
deliberately absent from the pool.

New functions in `harmony/functions.py` (naming per existing conventions):
`I6`, `I6add9`, `IV6`, `iv6` (borrowed minor iv — designed, the Romantic color
the user asked for; flagged designed because the brief found no period-chart
citation), `V9`, `II7`, `III7`, `VI7` (secondary-dominant chain), `#idim7`
(chromatic passing diminished between I and ii — inferred, standard period
practice per pedagogy sources).

`major_function_pool` (A sections):
`("I6", "I6add9", "ii7maj", "iii7", "IV6", "iv6", "V7maj", "VI7", "vi7", "#idim7", "II7")`

`bridge_major_function_pool` (B sections):
`("III7", "VI7", "II7", "V7maj", "V9", "iii7", "vi7", "ii7maj")` — built so the
rhythm-changes bridge `III7 → VI7 → II7 → V7maj` is reachable and favored (cited —
the "Sears-Roebuck bridge", brief §6).

Major mode has no bare `ii7`/`V7` — those names exist only in the minor spec
table — so both pools use `ii7maj`/`V7maj`. `V9` lives only in the bridge pool,
which keeps the A-pool at 11 names so it enumerates fully at length 4
(11⁴ = 14,641, under grammar's 20,000-combination cap) instead of being
stride-downsampled.

`function_pool` (minor, never selected at `p_major_center=1.0`): minimal valid
pool `("i7", "iv7", "V7")`.

New idiom shapes for `harmony/score.py` (canonicalized at construction like the
existing 18), all inferred from the period songbook unless noted:

- `I6 → vi7 → ii7maj → V7maj` (the golden turnaround)
- `I6 → #idim7 → ii7maj → V7maj` (diminished passing)
- `iii7 → VI7 → ii7maj → V7maj` (back-cycle)
- `I6 → iv6` (borrowed plagal color as a cyclic two-loop — designed; the
  four-chord `I6 → IV6 → iv6 → I6` form is grammar-inert since loops cannot
  start and end on the same function)
- `III7 → VI7 → II7 → V7maj` (bridge chain — cited)
- `I6 → II7 → ii7maj → V7maj` (V/V softening)

LIL table entries and avoid-note behavior follow existing rules; the sixth is a
chord tone, not a tension, so no new avoid cases beyond what `6add9` already
exercises. Calibration test: a small documented set of period progressions
(from the brief) must rank in the pool's top decile under the card's weights —
same method as faiyaz's 17-loop gate, scaled to what the brief cites.

## 3. Groove

**Stride keys.** New `keys_pattern: str = "comp"` field on `StyleCard`;
`groove/keys.py` branches on `"stride"`: beats 1 and 3 take a single low bass
note (loop root or fifth, register E2–G3, MIDI 40–55 — inferred, brief §3 found
no hard numbers so the register is synthesized from double-bass clearance and
period recordings), beats 2 and 4 take a mid-register close chord (C3–C5 zone
from the realized voicing). Right-hand figures ride the existing comping event
stream above. `p_keys_anticipation` gives the push; `keys_reattack` stays.

**Walking bass.** New `bass_feel: str = "riff"` and `bridge_bass_feel: str = ""`
fields; `groove/bass.py` branches:

- `"two"` (A sections): half notes, roots and fifths, the foxtrot two-feel —
  inferred, brief §4.
- `"walk"` (B sections): quarter notes; strong beats favor chord tones, beat 4
  takes a scalar or chromatic approach into the next downbeat (cited direction
  from walking-bass pedagogy, exact weights designed). Register E1–E3, MIDI
  28–52 — cited (double bass range, brief §4). Mono, like every bass stem.

The two→four switch across the bridge is the arrangement's lift. Ballroom sets
`bass_feel="two"`, `bridge_bass_feel="walk"`; existing cards keep `"riff"` and
render byte-identically.

**Brush drums.** All synthesized as deterministic sample files through the
existing `render/synth_perc.py` → kit → PlayBuf path (no new synthdefs; the
Boochi44 samples are not used by this card). Four new `DrumSound` entries —
`BRUSH_TAP`, `BRUSH_SWIRL`, `FEATHER`, `CHICK` — each with a seeded generator
in `synth_perc.py`, an empty `KIT_KEYWORDS` entry (never matched from
downloaded kits — synthesized only), and a GM note in `midi.DRUM_NOTE` for
previews. `load_kit` requires a file per `DrumSound`, so the same task that
adds the enum entries regenerates the local kit via `write_missing` — the
enum and the generators land together or every card's render breaks. A new
`ballroom_patterns` generator in `groove/drums.py` (same `{"A":…, "B":…}`
shape as the others) emits:

- `SNARE` — brush taps on beats 2 and 4 (`BRUSH_TAP`) over a swirl bed of two
  `BRUSH_SWIRL` hits per bar (designed timbre; pattern cited — brief §5).
- `KICK` — feathered quarter notes (`FEATHER`), whisper velocity, felt not
  heard (cited practice, brief §5; level designed).
- `HAT` — light chick on 2 and 4 (`CHICK`; inferred — early-30s kit practice).
- `PERC` — unused; `p_perc_bed = 0.0`.

**Pocket.** No new machinery, but the swing is not a direct offbeat-eighth
sweep: it manifests through the stride right-hand anticipations, which land
on the previous beat's swung "and" (tick − 480, then shifted by
`apply_pocket`'s existing `480 mod 960` swing rule); bass plays straight on
the beat, and brushes keep their grid placement with only the snap drag —
dance-band practice. Ballroom sets
`swing_band = (0.58, 0.68)` — designed; combo-recording measurements at this
tempo run higher (≈0.70–0.76, cited in brief §1) but dance-band charts sat
straighter, and no 1930s ensemble measurement exists (gap flagged in the
brief). Per-role feel: brush taps drag behind via `snap_rush_ms` set to a
positive band (the field is a range; positive means late), bass sits on the
grid, piano leans ahead through the existing anticipation channel — the
on-the-grid bass is a designed choice and documented as such, since the
literature contests it (Rose 1989 heard bass behind; brief §2).
`PocketReport` is unchanged; property tests measure the swing from MIDI onsets.

## 4. Strings

Strings get a new `Role.PAD` entry — the pad exists today only as a render
synthdef, not a role. The addition is backward-safe: only ballroom's
generators ever emit PAD events, so existing cards' JSON, MIDI, stems, and the
golden fixture are untouched (an empty role serializes to nothing). A new
generator (`groove/strings.py`), gated on a new `has_strings: bool = False`
card field, emits one sustained chord per harmony segment (minimum one bar), voiced from
the realized upper structure so the voicing DP's smooth voice-leading carries
over; register G3–E6 (designed). Tacet for the first A section — new
`pad_enters_section: int = 0` card field consumed by `arrange.py`: body
sections (intro and outro excluded) are numbered from 1 in timeline order, PAD
is muted in body sections numbered below the value, and 0 means always present.
Ballroom sets 2 (strings sit out the opening A only). Swells: each sustain carries
a rising expression ramp into the next downbeat, rendered as MIDI CC11 in the
fluidsynth path (depth designed; the arranging role — pads behind the rhythm
section — is cited, Whiteman-era practice, brief §7).

## 5. Render

**Voice map.** `_FLUIDSYNTH_KEYS_CARDS` and the keys-only special case in
`render/engine.py` generalize to a per-card role→soundfont table in
`render/stems.py`:

```python
_FLUID_VOICES: dict[str, dict[Role, str]] = {
    "molina":   {Role.KEYS: "piano"},
    "tunisia":  {Role.KEYS: "piano"},
    "ballroom": {Role.KEYS: "piano", Role.BASS: "gm", Role.PAD: "gm"},
}
```

`"piano"` resolves through the existing `_piano_sf2()` (YDP with GM fallback),
`"gm"` to the existing `_SF2` FluidR3 path. GM program numbers stay where they
already live — `midi._CARD_PROGRAMS` gains a ballroom row (KEYS 0, BASS 32
acoustic bass, PAD 48 string ensemble), and the program_change in the per-role
MIDI selects the patch. `render_keys_fluidsynth` becomes
`render_fluid_stem(beat, role, out_path)`; molina/tunisia argv and MIDI bytes
must be identical to today (their renders are released — the rerender guard is
the tripwire). Per-voice gain calibration is mandatory at implementation time, the
0.4.0 lesson: measure each fluid stem against the scsynth reference levels and
gate it (see §7).

**Bus.** `ballroom_bus` in `render/buses.py`: gentle glue compression
(Compander, low ratio — designed), single LPF at 14 kHz (designed — warm
ceiling, brighter than conductor, darker than molina), FreeVerb room_size 0.85 /
mix 0.24 / damping 0.4 (designed — the biggest room in the house). No crackle,
no wow, no bitcrush. Texture dials recorded in `card.texture` with provenance,
matching how the other buses are documented.

**Mix rows.** `_BALLROOM_ROWS` (dB, designed, calibrated at implementation):
KEYS −1.5, BASS −5, PAD −8, SNARE −14, HAT −16, KICK −15. PAD routes to the
keys bus (harmonic material shares the room). SUB and PERC never emit. The
master ceiling reuses the card's single `lpf_hz` texture dial (14 kHz,
designed — the engine passes one ceiling to both the card bus and
`master_out`, and ballroom follows that pattern).

## 6. Arrangement

AABA via `section_pattern` (§1). Intro: two bars of solo piano (existing intro
machinery), strings enter at the second section (§4), outro: existing ending
conventions. Two-feel A / walking B (§3) is the sectional contrast alongside
the bridge harmony.

## 7. Tests and gates

- **Theory**: `6`/`m6` interval spellings on the line of fifths; new function
  degree/quality mappings; `#idim7` spelling (sharp-one diminished resolves
  up — spelled with the sharp, never flat-two).
- **Grammar/calibration**: period progressions from the brief rank top-decile
  (§2); bridge pool reaches the dominant chain; AABA pattern emits A A B A.
- **Groove properties**: stride LH alternation invariant (odd beats single low
  note in 40–55, even beats chord); walking bass quarter grid, register 28–52,
  mono, approach-tone rule into downbeats; two-feel halves in A sections;
  swing ratio measured from MIDI onsets lands inside `swing_8ths` band; brush
  tap placement 2/4 with drag.
- **Render gates** (slow): ballroom master warm ceiling (energy above 16 kHz
  vs mids, threshold measured-then-locked like existing gates); cross-engine
  levels day one — bass and pad fluid stems within calibrated windows of the
  keys stem and the mix mid/low balance inside a band gated against molina's;
  determinism byte-identity for a ballroom render; tunisia/molina rerender
  byte-identity unchanged (voice-map refactor tripwire).
- **Golden fixture**: `faiyaz_seed7.mid` byte-identical (new card fields must
  default inert).

## 8. Out of scope (the card's future, not its birth)

Melodic lead-line generator, string countermelodies, rubato/tempo curves, and
sampled orchestral voices (VSCO2-CE upgrade path — voices swap in the render
layer later and the catalog re-renders itself). `Role.PAD` and the four brush
`DrumSound` entries are the only model-layer additions.

## 9. Risks

GM string ensemble and acoustic bass are serviceable, not luxurious; the bus
(LPF + room) is designed to flatter them, and the upgrade path exists precisely
because timbre is the card's weakest layer. The swing pocket is the first
systematic-offset transform in the engine — property tests pin it before any
listening judgment. Fluidsynth CC11 handling for swells is assumed from the GM
spec; if expression proves unresponsive in NRT, swells fall back to per-note
velocity ramps (same musical intent, coarser grain).
