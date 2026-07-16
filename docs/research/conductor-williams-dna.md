# Conductor Williams — Production Technique Brief

Research input for the Lattice spec. Compiled 2026-07-15 from primary sources (his own
video breakdowns, interviews) and community reverse-engineering.

**Confidence labels:** **[EST]** = established, sourced to Conductor himself or verified
documentation. **[COMM]** = community reverse-engineering (plausible, unconfirmed by him).
**[INF]** = inference from the evidence.

## 0. Premise corrections

- **No credit on Kanye's *Vultures* 1 or 2.** "BURN" was Azul/Beam/Chrishan/Rissi sampling
  Band of Thieves (1976, cleared via Tracklib). Conductor confirmed in Billboard he hadn't
  worked with Kanye. Real mainstream placements: Drake ("8AM in Charlotte," "Stories About
  My Brother"), J. Cole ("7 Minute Drill," with T-Minus), Tyler, The Creator ("SIR
  BAUDELAIRE," reusing his Westside Gunn beat).
  https://www.tracklib.com/blog/kanyewest-tydollasign-vultures-allsamples
  https://www.billboard.com/music/rb-hip-hop/conductor-williams-producer-griselda-tyler-the-creator-1235960539/
- Commonly misattributed: Westside Gunn "Julia Lang" (Camoflauge Monk), "Science Class"
  (Swizz Beatz), Mach-Hommy "The 26th Letter" (Denny LaFlare), Benny "BRON" (Hit-Boy).
- Identity: Denzel Williams, b. 1982, Kansas City MO; ~20 years an actual freight-rail
  conductor before going full-time post-*Pray for Paris* (2020). **Berklee-trained in
  mastering**, ran his own studio (The Depot) from 2015 — the lo-fi is a choice by a
  trained engineer, not naivety.
  https://en.wikipedia.org/wiki/Conductor_Williams
  https://djbooth.net/features/how-conductor-williams-left-a-20-year-career-to-make-beats-full-time-060225/

## 1. Signal chain and gear

**[EST] Chronology (his own videos):** Korg Triton LE (~2002) → **MPC 2000XL** (2005, only
machine until ~2016) → **Boss SP-303 + Roland SP-606** from ~2016 → **Akai MPC One** added
2021 ("right before Hitler Wears Hermes 8"), now the deadline go-to. Also an Ensoniq
ASR-10. Rejected the MPC Live over ergonomics.
https://www.youtube.com/watch?v=W1YQJDnq7ME · https://www.youtube.com/watch?v=aATFsALiWEc
https://www.rollingstone.com/music/music-features/rome-streetz-conductor-williams-interview-trainspotting-1235351285/

- **[EST] Which classics on which box:** "Michael Irvin" last beat made only on the 2000XL.
  "Spoonz," "Peppas," "Frank Murphy," "Mariota," "Danhausen," all of Rome Streetz *Kiss the
  Ring*: MPC One + SP-606. *Trainspotting* (2025) on "the little groove boxes… there's no
  multi-tracks."
- **[EST] Two-machine rig + 2-track bounce:** drums from the MPC One, sample sequenced and
  effected on the SP-606, whole beat bounced as a stereo 2-track into Pro Tools. No
  multitracks; he admits for half of requested breakdowns he "either doesn't have trackouts
  or never saved the beat."
- **[EST] Print-to-tape, no revisions:** "Once it's in the machine and to tape? I'm not an
  edit guy… That s—t is cooked." (Billboard). Corroborated by collaborator Samy Deluxe:
  "He overdubs the beats… onto tape and lets it run through the tape to create slight
  distortion. It's not a plugin but an analog step."
  https://thecircle.de/en/blogs/features/samy-deluxe-im-interview-ueber-sein-album-mit-conductor-williams-und-die-evolution-des-hip-hop
- **[EST] Mixing stance:** essentially none after the machine; mastering outsourced (Dave
  Cooley — J Dilla's *Donuts* — mastered *Trainspotting*: "it may not be polished, it might
  be matte").
- **[EST] SP-606 technical profile:** 44.1kHz; 16 velocity pads; 4-track sequencer at
  **96 PPQN**, swing as a pattern-edit option; **chop = max 16 segments**; BPM-sync
  time-stretch with audible "crunchiness and unwanted artefacts" outside a narrow range
  (Sound on Sound); 45 MFX incl. **032 Vinyl Simulator, 007 Lo-Fi Processor, 004 Tape Echo,
  005 Isolator, 001 Filter+Drive, 006 Compressor**; 2-band mastering compressor.
  https://www.soundonsound.com/reviews/roland-sp606

## 2. Sampling — what and how

**[EST] Source policy, his words:** "If I sample off YouTube, or only vinyl, or sample
packs — the answer to all of those questions is yes." Records restaurants, atmospheres,
VCRs. "Does it make a sound, and can I record it."
https://www.youtube.com/watch?v=5BH9hYekVZQ

**[EST] Documented flip corpus (WhoSampled-verified, key entries):**
- **Jazz/fusion dominates:** Billy Cobham "Siesta/Wake Up!!!" 1976 → "Michael Irvin"/"SIR
  BAUDELAIRE"; Sun Ra → "Euro Step"; Julius Hemphill (free jazz) → "Danhausen"; Joe Farrell
  (CTI) → "Joe Pesci"; Joachim Kühn/Alphonse Mouzon 1976 → Conway "Noir"; Quincy Jones →
  Boldy "The Ol Switcharoo"; David Axelrod → Rome Streetz "Heart on Froze"; Bobby
  Hutcherson → "Hold You".
- **Soul/gospel:** Margie Joseph (Volt 1970) → Conway "Flame"; Valentine Brothers → "God Is
  Love"; Larnelle Harris (gospel) → "Spoonz"; The Finishing Touch → "Munch".
- **Left-field signatures:** Crystal Gayle "Sneakin' Out the Back Door" (1979, country)
  flipped **three separate times**; Japanese jazz-fusion (Bingo Miki, Emiko Nakayama);
  Euro library/pop; Swedish alt-rock; soft rock (Bread → "Self Luh").
- **Ephemera garnish:** MJ "Thriller" vocal stabs (4+ tracks), Jay-Z vocal drops, CNN/TMZ/
  wrestling/Wild Style dialogue, a Mercedes GLA door chime.
- **Decade skew [EST]:** overwhelmingly 1970s, some late-60s/early-80s.
  https://www.whosampled.com/Conductor-Williams/

**[EST] The modern-library pipeline (under-appreciated):** big-artist placements mostly
sample *contemporary analog-recorded "fake vintage" libraries*, not old vinyl — Polyphonic
Music Library "A Faithful Spirit BPM 59" (100% analog gospel pack) → Drake "8AM in
Charlotte"; Jimmy Q "Maze" → Drake "Stories About My Brother" (via Tracklib); Frollen Music
Library → Leon Thomas "FEELINGS ON SILENT"; Napes packs → "Suicide in Selfridges" and
*Trainspotting*; Soul Surplus → "Self Luh". 2025 clearance mantra: "use the humans" —
musicians replay/interpolate, "then I'll manipulate it… I'm essentially making two beats."
https://polyphonicmusiclibrary.com/products/a-faithful-spirit
https://www.tracklib.com/blog/hottestflips-bestof2024-samples-beats

**[EST] Selection criterion is affect + texture, not theory:** "I don't look with my eyes
or my ears. I look for something that feels like how I'm feeling… I'm only going for
texture and feel… and then I manipulate." Inspiration from film, painting (Duchamp,
Virgil Abloh's 3% rule) rather than music.
https://www.youtube.com/watch?v=h1WGnMDcqAY

## 3. Chop mechanics

- **[EST] Pad-to-pad copy-paste chopping (his named core technique, from the ASR-10):**
  duplicate the *entire* sample across successive pads, then destructively trim/modify each
  pad into a different chop — "you copy your sample from key to key… modifying the sample
  as you go… It's manic." Loop-derived chopping, not auto-slice: every pad starts life as
  the whole loop.
- **[EST] Loop-first listening:** runs the loop "like a weirdo… inside of that loop I cut
  my chops — I cut out all the parts that I like." Spectrum per track from near-readymade
  ("Stories About My Brother": "straight up sample the joint… it's about context… slight
  manipulation" — Duchamp readymade doctrine) to "drunkenly chopped" mosaics ("BDP").
- **[EST] Pitch-shifting: empirical, small, global.** "Just pitching it up by one felt
  good, so let's just do it to all of them." Pitched-up "chipmunk choir" on "8AM in
  Charlotte."
- **[EST] Time-stretch:** prizes MPC One real-time stretch "to hold on a phrase or chop on
  a vowel of a vocal." **[COMM]** A studied beat did NOT stretch a 172 BPM loop — he nudged
  beat tempo so chops land off the downbeat (old no-timestretch MPC trick).
  https://www.youtube.com/watch?v=whIGsWcelyA
- **[EST] Filtering:** SP-606 Isolator + Filter+Drive in every chain; Griselda house recipe
  is low-pass "vintage muffle." **No evidence of stem separation** — takes the full mixed
  texture and EQs around it. [INF]
- **[EST] Tempo anchors:** ~86 ("SIR BAUDELAIRE"), ~85–88 ("7 Minute Drill"), ~88
  (Selfridges era), 97 ("8AM in Charlotte"). **[INF] Model range: 80–100 BPM, half-time feel.**

## 4. Texture and lo-fi character

- **[EST] Named devices:** SP-606/303 **Vinyl Simulator** + Lo-Fi Processor + real tape
  print + sources that are already dusty. **[COMM] strong consensus:** the audible
  wow/flutter warble is the SP vinyl sim, whose compressor also "ducks" the program — the
  pumping glue. https://www.reddit.com/r/mpcusers/comments/1ewyc02/
- **[EST] "Ugly" as doctrine:** "let's see the type of ugly we can get out of this… all of
  the clicks and bells and the knocks and the grime… I just love." Slang for saturation is
  "grits." Broken gear welcomed ("a lot of my buttons are broke… I get a whole nother
  desired sound"). "The sonics are very polarizing, which is good."
- **[EST] Anti-digital stance:** "I don't like computers like that. I don't like synthetic
  sounding music." Computer appears only as a tape deck.
- **[INF] Net texture model:** stacked generations of degradation — (already-dusty source)
  → sampler color → vinyl-sim wow/flutter + compressor pump → tape overdub → "matte"
  mastering. No bitcrusher-as-effect; the crunch is device-native. Artifacts (stretch
  crunch, clicks, truncation ticks) are kept, not cleaned.

## 5. Drums

- **[EST] Largely sampled breaks, dug cheap:** "Been hunting drum breaks from dollar bins."
  **[COMM]** drums behave like processed loops fired from the MPC One, not dense one-shot
  programming.
- **[EST] Programming sparse and reductive:** "Self Luh" = "Just a flip, some effects, and
  a kick-snare 1-2." Drake beat = "a kick and a rim shot… simple pattern, bro," one ride
  placed "in a space Drake didn't need." Selfridges: ghost kicks "to thicken," one "big
  bass note to really shake the listener." Target reference: "that '93–'94 energy… drums
  almost kind of hollow, smack of a drum."
- **[EST] Drumless is a first-class mode:** "Michael Irvin" — "no kicks, no snares. Warm,
  very golden… I wanted it to be a score. Like a noir." "Frank Murphy" 8-minute drumless.
  NPR: "loop-heavy, dissonant and often devoid of bass."
- **"Famously heavy Griselda drums" partially a misconception for him [INF]:** knock comes
  through saturation/transient grit at moderate density, sitting *with/under* the sample.
  Sub-bass frequently absent; when present, a single "big bass note." J. Cole added his own
  sine bassline under "7 Minute Drill" and asked permission first.
- **[EST]** "The drums on his MPC 2000 hit way harder than his MPC One" (his claim).

## 6. Structure, loops, arrangement

- **[EST] Composition order: melody first.** "I always start with the melodies first… I
  hold the drum pattern in my head" (beatboxes into his phone to retain it). Drums last.
- **[EST] One-pass, performance-committed:** no post-editing; hand-played sections with
  mistakes kept (Selfridges outro flub — Gunn kept it). Arrangement tools = mute/unmute and
  pad re-performance. **[INF]** Variation = chop-order permutation, dropouts, filter/FX
  moves, tag placement — not new parts.
- **[EST] Track lengths:** commonly ~1:30–2:30, no hooks ("SIR BAUDELAIRE" is 1:29);
  outliers long ("Frank Murphy" 8 min). Album pacing: beats sequenced to "snap against each
  other" like film cuts. Beat tapes: 15–20 instrumentals every 1–2 months.
- **[EST] The tag as arrangement element:** real viral video (man hammering a DC Metro
  intercom, Dec 2015), deployed like a mixtape DJ drop — "obnoxious… like a graffiti
  artist" — often mid-beat as a percussion/energy event.
  https://knowyourmeme.com/memes/conductor-we-have-a-problem
- **[EST] Batch workflow:** historically 5–10 beats/day; artists pick from batches (Gunn:
  "I can listen to literally 100 beats and pick two").

## 7. Harmony

- **[EST] What sources hand him:** 70s jazz-fusion/CTI (maj7/9/13, modal vamps),
  gospel/soul (I–vi gospel motion, plagal turns, choir voicings), deliberately "wrong"
  material (Sun Ra, free jazz) where dissonance is native. Modern-library gospel is the
  mainstream-placement palette.
- **[EST] Values harmonic motion but sources it rather than plays it:** Drake brief — "I
  wanted basslines, **a chord change**, jazz and soul."
- **[EST] Two documented harmony manipulations:** (1) global semitone re-pitch by ear
  (transposition, harmony preserved); (2) chop-order recomposition, which can break the
  source progression ("key-altering trumpets" on "Frank Murphy," "drunkenly chopped" vocal
  harmony on "BDP").
- **[INF] Engine model: harmony-preserving at the bar scale, harmony-agnostic at the chop
  boundary** — chops selected by timbre/feel, may butt-splice non-adjacent chords without
  voice-leading correction; dissonant overlaps kept if the texture feels right. No evidence
  of per-chop re-pitching to build new progressions (Dilla/9th Wonder style).

## 8. Timing and feel

- **[EST] Groove is inherited + performed, not programmed:** drums arrive as breaks (groove
  embedded in audio); chops performed pad-to-pad "manic[ally]"; sections hand-played with
  mistakes retained.
- **[COMM]** Community consistently hears unquantized, off-kilter/drunk placement.
- **[INF] Pocket model:** kick/snare grid is the source drummer's (behind-the-beat 70s funk
  feel); chops land slightly late/early from live pad performance; tempo-nudge trick adds
  systematic off-grid placement. **No source states a swing percentage — encode performance
  jitter + break-native groove, not a fixed swing value.**

## 9. Canonical quotes

- "Does it make a sound, and can I record it."
- "I'm only going for texture and feel… then I manipulate."
- "Copy your sample from key to key… modifying as you go… It's manic."
- "Once it's in the machine and to tape… I'm not an edit guy… That s—t is cooked."
- "No kicks, no snares. Warm, very golden… I wanted it to be a score. Like a noir."
- "The innocence of not knowing but being willing to experiment is how you get magic."
- "There's times where I'm cutting a sample and I gotta turn the machine off, because it's
  going Dilla World."
- "Use the humans… I'll manipulate it… I'm essentially making two beats."

Primary mining veins: his YouTube "HOW I MADE…" breakdowns (Selfridges: jqNPtHjHgjo;
Stories About My Brother: FX_TDJO7rik; FEELINGS ON SILENT: Oh5RTP4wLgA), gear essays
(W1YQJDnq7ME, aATFsALiWEc, 55mPLc2vnaY), Patreon streams, Dealer's Choice (Feb 2026,
hhCbwtW3igU), DJBooth (Jun 2025), Rolling Stone (May 2025), Billboard, NPR The Formula.

## 10. Engine cheat-sheet ([INF] parameterization)

1. **Source:** one 2–8-bar excerpt of a 1968–82 jazz-fusion/soul/gospel record (or
   analog-recorded pastiche), full mix, no stem separation; ~15% left-field wildcard.
2. **Prep:** global transpose ±1–2 semitones by ear; optionally speed-change without
   timestretch so chops displace onto offbeats; low-pass muffle / isolator carving.
3. **Chop:** duplicate loop across 8–16 pads; per-pad trims of different lengths (downbeat
   phrases, vowel-cut fragments, one-shot stabs); perform order live with jitter; allow
   splices across chord boundaries, no voice-leading fix.
4. **Drums:** either none (score mode, ~15–20% of catalog) or a dollar-bin break plus
   minimal overdubs — kick + rimshot "1-2," ghost kicks, one ride in a gap, occasional
   single low bass note; level with/under the sample, dry, mid-forward, no sub emphasis;
   80–100 BPM.
5. **Degrade (in series):** sampler color → SP vinyl-sim wow/flutter + pumping compression
   → tape pass → no corrective mixing; keep clicks, stretch crunch, truncation errors.
6. **Arrange:** 1:30–2:30, loop-dominant; variation via mutes, drum dropouts, filter moves,
   hand-played mistake moments, shouted tag as mid-track event; commit in one pass, never
   revise.
