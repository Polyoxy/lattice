# Chase Card — Design

Heartbreak at highway speed: a night-drive single and the sixth style card.
Minor keys, 150–170 bpm, the lament descent under a modern pulse. Grand piano
duelling itself, a string section that answers instead of cushioning, and a
solo violin that takes the bridge. The emotional mechanic, by user direction:
both voices tried — the answer always echoes the call and then twists it,
displaced, bent, cut short. Resolution keeps being refused.

Decisions locked with the user: escalation arc (piano duel → strings answering
→ violin solo bridge → everything at once), sleek modern pulse under the
orchestra (tight hats, rim, sub weight — no vintage dust), motif-DNA line
engine (approach B: card-carried motif shapes, generated answers).

## 1. The card

`CHASE: Final = StyleCard(...)` in `cards.py`, registered like the others.
Minor only.

| Field | Value | Provenance |
|---|---|---|
| `p_major_center` | `0.0` | designed — heartbreak lives minor |
| `centers` | `("Dm", "Gm", "Cm", "Fm")` | designed |
| `major_centers` | `("C",)` (never selected) | designed |
| `bpm_range` | `(150, 170)` | designed — highway pulse |
| `loop_len_weights` | `((2, 0.3), (4, 0.7))` | designed |
| `has_bridge` | `True`, `section_pattern="AABA"` | the solo needs a home |
| `keys_pattern` | `"duel"`, `bridge_keys_pattern="duel_low"` (new field) | designed |
| `bass_feel` | `"riff"` (existing; gives SUB weight + sparse BASS) | designed |
| `p_bass_stab` / `p_bass_approach` / `p_bass_glide` | `0.15 / 0.2 / 0.3` | designed — sparse |
| `pad_pattern` | `"answer"` (new field, default `"sustain"`) | designed |
| `has_strings` | `True`, `pad_enters_section=2` | strings join at A2 |
| `has_lead` | `True` (new field, default `False`), `lead_enters_section=3` (new field, default 0) | violin from the first B onward |
| `swing_band` | `(0.5, 0.5)` | designed — dead straight, the road doesn't swing |
| `snap_rush_ms` | `(0.0, 0.0)` | designed — dead-straight rim, not dragged; corrected in task 11 (was `(-4.0, 0.0)`, `apply_pocket`'s snap branch never covered RIM) |
| `timing_sigma_ms` | `2.5` | designed — machine-tight, human-warm |
| `p_transpose_event` | `0.0`, `target_len_s=(180, 225)` | designed |

New `StyleCard` fields, all inert-default: `bridge_keys_pattern: str = ""`,
`pad_pattern: str = "sustain"`, `has_lead: bool = False`,
`lead_enters_section: int = 0`, `motifs: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...] = ()`.
Ballroom keeps `pad_pattern="sustain"` implicitly; the golden fixture and
every released card stay byte-identical (fields only act when set).

Serialization note, load-bearing: `rerender._convert_field_value` currently
reconstructs only two levels of tuple nesting — `motifs` is three deep, so
the converter must become recursive in the same task that adds the field, or
every saved chase beat false-positives the drift guard. A round-trip test
(chase beat → json → rebuild → byte-equal json) is mandatory.

## 2. Harmony — the lament spine

`function_pool`:
`("i7", "i9", "iv7", "iv9", "bVII7", "bVImaj7", "V7", "V7b9", "v7", "iim7b5")`
— all existing minor functions; no new specs needed. `bridge_function_pool`:
`("i7", "iv9", "bVImaj7", "V7b9", "iim7b5", "bVII7")`, `bridge_len_weights=((2, 0.5), (4, 0.5))`.
`allow_tritone_sub=False`, `allow_chromatic_mediant=True`.

New idiom shapes (`_RAW_IDIOM_SHAPES`), the heartbreak book:

- `i7 → bVII7 → bVImaj7 → V7` (the lament descent — cited: the descending
  tetrachord is the canonical lament figure; ballroom-dna's citation
  discipline applies, source recorded in the shape comment)
- `i7 → bVII7 → bVImaj7 → V7b9` (the descent with the sting)
- `i9 → iim7b5 → V7b9` (the plea)
- `i7 → iv9 → bVII7 → bVImaj7` (leaving without the V — designed)

Cross-card safety is a hard requirement, and token disjointness cannot
provide it here: `bVII7` and every other name in these shapes already appear
in existing minor pools (conductor pools `i7/bVII7/bVImaj7/V7` outright), so
global shapes would silently re-rank existing cards' music. The mechanism
therefore changes: `harmony/score.py` gains card-scoped shapes —
`CARD_IDIOM_SHAPES: dict[str, frozenset[tuple[str, ...]]]` — and
`loop_score` awards the idiom bonus when the canonical rotation is in the
global set OR the card's own set. The global set is untouched; existing
cards are bitwise-unaffected (locked by the golden fixture, the released-card
rerender suite, and the slow calibration gates, all of which must stay
green). Chase's four shapes live only in its scope. A chase calibration gate
locks the two lament shapes into the top decile of the length-4 pool, same
method as ballroom's.

## 3. The line engine — `groove/lines.py`

The first melodic subsystem. One module, three consumers (RH strikes, violin
solo, string answers).

**Motif DNA.** `card.motifs` carries designed shapes as
`(intervals, rhythm)` pairs: `intervals` are line-of-fifths offsets from the
current chord root (validated against the avoid-note table at realization —
the existing constraint machinery is the melodic filter); `rhythm` is slot
offsets within a 2-beat window (slots of 480 ticks). Chase ships five,
provenance designed, named in comments: the sigh (falling minor third), the
cry (5–♭6–5), the spiral (descending run 8–♭7–♭6–5), the push (repeated root
anticipating), the defiance (rising 5–♭7–8).

**Realization.** `state_motif(motif, segment, register, rng) -> tuple[Event, ...]`:
anchor the intervals to the segment's chord root, spell on the line of fifths,
place at the window's slots, velocity arc rising into the last note. Any note
failing the avoid-note check resolves to its nearest chord tone (never
dropped — the line stays intact).

**The denial.** `answer_motif(call_events, transform, segment) -> tuple[Event, ...]`
with five transforms, chosen per answer by rng: `displace` (+480 ticks — she
answers late), `truncate` (drops the last note — she doesn't finish it),
`bend` (final interval pulled down a scale step — same words, wrong meaning),
`mock` (whole line a scale step up — thrown back), `deny` (final note replaced
with an unresolved second — never lands). Answers voice in a different
register/role than the call. A property test asserts every answer is
derivable from its call by exactly its named transform.

**Conversation layout.** Per 2-bar span: call window (beats 1–2 of bar 1),
answer window (beats 3–4 or displaced into bar 2). In A sections the call is
piano RH, answers alternate strings and violin (`pad_pattern="answer"`:
the strings carry the monophonic answer line itself, instead of sustains), and
each voice's answers are silent until its entrance (A1: all answers muted —
he talks to himself; A2: strings only; from the first B: both). In B
sections the call is the violin (`Role.LEAD`), answers
alternate strings and piano RH. Density:
one exchange per 2 bars in A, every bar in B (the solo argues harder).

## 4. The duel keys

`keys_pattern="duel"` in `groove/keys.py`: LH is the motor — relentless
straight-8th ostinato, register MIDI 40–52, cycling root→5th→♭7→5th per
chord (chord-derived via `fifth_interval` and the seventh when present);
velocity pulses (accent beat 1 and the "and" of 2). RH carries the line
engine's call/answer events plus off-window stabs (two-note voicing
fragments from the realized stack, mid register 60–76). `"duel_low"` (bridge)
keeps the full LH motor and RH plays only the line engine's answer events —
no calls, no stabs; the violin owns the melody there. Anticipation channel unused (`p_keys_anticipation=0.0` — the
duel's rhythm is written, not drifted).

## 5. Ensemble, arrangement, escalation

- **Role.LEAD** (new enum value `"lead"`, midi channel 4) — backward-safe
  exactly as Role.PAD was: only chase emits it. Solo register MIDI 67–91
  (violin cantabile), above the RH stab zone so the duel never blurs. Fluid voice GM program 40
  (violin), with the existing CC11 swell machinery on its sustained notes.
- **Escalation by entrances** (all existing machinery + one mirrored field):
  intro (piano solo, 1 cycle) → A1 duel + pulse (`pad_enters_section=2`
  mutes strings in body 1) → A2 + string answers → B violin solo
  (`lead_enters_section=3` = first B in AABA) → A3+ everything. LEAD stays
  in from the first B on — the final stretch is the full fight.
- **Drums** — `chase_patterns` in `groove/drums.py` using the existing kit
  sounds (no new DrumSounds): KICK on 1 plus a sparse rng extra, RIM
  cross-stick on 3, HAT tight 8ths with a velocity wave, B-variant doubles
  hat density. PERC empty. (`parts_b` never plays for bridge cards — the
  variant exists for shape-consistency only, same as ballroom.)
- **Bass** — existing riff feel: SUB sustained roots (the weight), BASS
  sparse octave figures. No bridge feel switch — the road doesn't stop.

## 6. Render

- Fluid voices: `"chase": {Role.KEYS: "piano", Role.LEAD: "gm", Role.PAD: "gm"}`;
  `_CARD_PROGRAMS["chase"] = {KEYS: 0, BASS: 33, SUB: 38, LEAD: 40, PAD: 48}`.
  LEAD routes to the keys bus in the mix (harmonic material, one room).
- `chase_bus` in `buses.py`: light glue (Compander, `glue_db=2.0`), LPF
  16 kHz (night-glass, the brightest card ceiling), FreeVerb room_size 0.35 /
  mix 0.12 / damping 0.5 (tight room, not a hall). No crackle, no wow.
- Mix rows (designed, calibrated at implementation): KEYS −2, LEAD −3,
  PAD −9, BASS −6, SUB −4, KICK −6, SNARE −10 (rim), HAT −11.
- Master ceiling = the card's single `lpf_hz` dial (16 kHz), engine pattern.

## 7. Tests and gates

Property: motif realization anchors to chord tones (avoid-note filter
proven); answer-transform derivability; duel LH ostinato coverage (every
8th slot filled, register 40–52); escalation entrances (LEAD absent before
body 3, present after; PAD from body 2); conversation windows (calls and
answers never overlap in time within a section). Slow gates
measured-then-locked at production config (a minor center, in-band bpm):
brightness (corrected in task 11 — measured darker than ballroom's
same-seed ratio, not brighter as originally assumed; ballroom's brush kit
is broadband-noisy in the 16–21k band regardless of either card's LPF
dial, so the relative gate locks the true direction plus an absolute
ceiling sanity), LEAD/PAD/KEYS stem level windows, determinism
byte-identity. Golden fixture and released-card rerender suites are the
standing tripwires.

## 8. The single

One track ships first (the special), full wording gate as always. The three
generated candidates get auditioned locally before anything goes public.

## 9. Out of scope

Multi-instrument counterpoint beyond call/answer (no fugues), tempo
automation/rubato, sampled solo violin (GM now, VSCO2-CE upgrade path
unchanged), lead lines for existing cards (the engine is built card-gated;
backporting duel/answer patterns to ballroom is a later decision).

## 10. Risks

GM solo violin is the weakest timbre in the plan — mitigations: CC11
expression, the tight room, and the mix keeping it forward but blended; the
upgrade path exists. The line engine is new ground — motif DNA keeps the
melodic floor high, and every emotional mechanic (late, cut, bent, mocked,
denied) is a deterministic transform with a property test, not a hope.
