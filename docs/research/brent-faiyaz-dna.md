# Brent Faiyaz — Production DNA Brief

Research input for the Lattice spec. Compiled 2026-07-15.

**Reliability key:** CITED = a source states it (URL given). INFERRED = deduction from
cited data. Chord data from Ultimate Guitar tabs (parsed from embedded JSON), one
Hooktheory Theorytab (re-verified in raw markup: `data-tonic="A" data-scale="minor"`,
144 BPM), Chordify/ChordU/GuitarTuna detections, KVR analyses. BPM/key figures are
Spotify-analysis-derived (Tunebat/SongBPM/Musicstax share the upstream source — agreement
≠ independent measurement). One source (studiotalksevents.com NDK interview) flagged
LOW-CONFIDENCE throughout.

**Premise corrections (verified negatives):** Rogét Chahayed has **no** Brent credit —
"Gravity" is DJ Dahi alone, Steve Lacy *playing* guitar, not a sample. "Jonah Christian"
has no Brent credit — the actual collaborator is **Jonah Roy** (drums). "Missin You Crazy"
is Russ. No Brent song called "Lost" (2018 EP title). "Poison" is from *A.M. Paradox*
(2016), not *Sonder Son*.

## 1. Harmony — per-song data (core tracks)

| Song | Key (functional) | BPM (felt) | Progression | Reading |
|---|---|---|---|---|
| **Trust** (2018) | F minor (Ab tag) | 92 | **Dbmaj7 → Fm7**, two chords, whole song | ♭VImaj7→i7 Aeolian |
| **Dead Man Walking** | A minor | ≈72 | **F → Em** (Fmaj7/Em7), whole song | ♭VI→v around an **implied Am never stated** |
| **Rehab (Winter in Paris)** | A minor (Hooktheory+UG; Spotify says F major — conflict, weight A minor) | ≈72 | **i7(no3) → v** both verse AND chorus; verse 4 opens F→Dm | Pure Aeolian 2-chord loop, **minor v, no leading tone** |
| **Wasting Time** (Neptunes) | G minor | 89 | **Gm–Am–Dm** intro; **Gm–Am–Bb–Dm** + Eb verse (others: Gm7/Am7/Dm7/Ebmaj7) | i–ii–v with natural ii (**Dorian**); Eb(maj7) = the Neptunes lift |
| **Poison** (2016) | D minor | 117 | **Dm–Am–Dm–Am–A7** every section | i–v Aeolian loop + **harmonic-minor V7 kicker** each cycle |
| **Clouded** | D major | 65 | **Dmaj7→C#m7→F#m7→Em→Dmaj7→Em→A7**, then mostly Dmaj7↔C#m7 | Imaj7–vii(m7)–iii7–ii7–V7; C#m7 non-diatonic half-step-under-tonic shimmer |
| **All Mine** | A major tag | ≈71 | **C#m → D** vamp (+Bm) | iii–IV shimmer, or **C# Phrygian i–♭II** — half-step root move IS the hook |
| **Gravity** (DJ Dahi) | E major (C#m tag) | ≈82 | sounding **F#m9 → B7 → Emaj7 → C#m7** | **ii9–V7–Imaj7–vi7** — jazz ii–V–I loop parking on relative minor |
| **Jackie Brown** | Gm-anchored (Bb tag) | ≈69 | detector pools Gm/Bb/F/Eb/Cm; producer short says "only two chords!" | most-conflicted; likely 2-chord Gm guitar loop smeared by detectors (INFERRED) |
| **Rolling Stone** | B minor | ≈70.5 | **Em6add9 → Em9 → F#m7 → Bm7 → Gmaj7** identical verse 1 / chorus / verse 2 | **iv(6/9)–v7–i7–♭VImaj7** Aeolian; from Em it spells **E Dorian**. Most extension-dense cited loop |

Secondary (all CITED): **Talk 2 U** — Cm: **Cm7→Fm7→G7♭13** loop, bridge Abmaj7–G7–Cm7
(i7–iv7–V7♭13, jazziest recurring cell). **Stay Down** — G#m: G#m7, **A#m7 (Dorian natural
ii)**, D#7 (harm-minor V7), Emaj7, **D#aug** — most through-composed. **Show U Off** — Am:
**Am7–F–Dm7** (i7–♭VI–iv7). **Been Away** — Gm tab (Cm/Gm/Eb/Dm + **borrowed D-major V**),
chromatically modulating outro. **Make It Out** — Bm with **both IV7 (E7, Dorian) and iv7
(Em7)** in one loop = modal mixture. **Price of Fame** — **G#m→A** half-step vamp (same
device as All Mine), 71 BPM. **Loose Change** — C#m: **F#m–G#m–A(maj7)** = iv–v–♭VImaj7
ascending, **tonic chord never stated**.

Sources: tabs.ultimate-guitar.com (Trust 3957022, DMW 3398486, Rehab 3040749, Poison
3347672, Clouded 3144785, Gravity 4011955, Rolling Stone 5772473, Talk 2 U 2250737, Stay
Down 5749121, Show U Off 3607442, Been Away 3243761), hooktheory.com/theorytab/view/brent-faiyaz/rehab-(winter-in-paris),
chordu.com, guitartuna.com, chordify.net, mychords.net, songbpm.com, tunebat.com,
https://www.kvraudio.com/forum/viewtopic.php?t=610809 (Upset Feet: whole song on one
m7/9 stack D–F–A–C–E, sampled and transposed).

## The harmonic fingerprint (synthesis)

- **Loop-based vamps, not progressions.** 2–4 chord loops; **verse harmony = chorus
  harmony** (Hooktheory shows identical progression for both Rehab sections; every UG tab
  repeats one cycle).
- **Minor default; Aeolian home.** Functional centers: Fm, Am, Dm, Cm, Gm, G#m, C#m, Bm.
  Recurring colors, all cited: **Dorian natural-ii** (Stay Down, Rolling Stone, Wasting
  Time, Make It Out), **Phrygian/♭II half-step vamps** (All Mine, Price of Fame),
  **harmonic-minor V7 spice as loop kicker** (Poison A7, Talk 2 U G7♭13, Stay Down
  D#7/D#aug, Clouded A7).
- **The minor v is a signature.** Hooktheory's most-used chord for Rehab is **v** —
  dominant function without a leading tone. Same in Poison, Rolling Stone, Loose Change,
  DMW.
- **Extensions constant:** m7, m9, maj7, add9, 6add9, 9, 7♭13, aug — in the tabs
  themselves. ChordMap: **Imaj7–iii7–vi7–IVmaj7** = "the Daniel Caesar and Brent Faiyaz
  sound" (https://chordmap.io/blog/rnb-chord-progressions-guide).
- **Tonic avoidance/ambiguity is a feature:** DMW and Loose Change never state the tonic;
  Trust and All Mine hover between relative readings — why key databases split.
- **What he does NOT do (per evidence):** no tritone subs, no chromatic mediants in any
  cited tab/analysis (absence INFERRED). Secondary/borrowed dominants: yes. Modal
  interchange: yes. **Whole-loop transposition as harmony** is documented: piano loop
  "pitched down by five semitones, creating that one-five progression over a 16 bar loop"
  (Hix https://www.youtube.com/watch?v=iGcNrlzBgb8).

## 2. Voicing and register (thinnest-sourced area)

- **Close-position stacked 7ths, mid register.** OG Chizzy teaches m7 as "2-3-2 spacing,"
  maj7 "3-2-3," add a 9th for tension (https://www.youtube.com/watch?v=cTbOWm7gWPs). KVR:
  D–F–A–C–E five-voice close stack. Keys/guitar ≈ C3–C5; Rehab melody A3–D5 (Hooktheory).
  Exact per-record registers: INFERRED, unmeasured.
- **Bass instrument carries the root; keys float above.** Sub "just following the root
  notes" (bangagurl https://www.youtube.com/watch?v=w_wa32HmDSs); "passing notes just on
  the bass guitar" (Hix). Rootless upper voicings functionally common — INFERRED.
- **Guitar signature:** "a chord up and a note slide" with wah-ish effect + pitched-down
  (−2 st) double (Hix). "What defines this chord progression is actually the passing notes
  played in between" (VLTN https://www.youtube.com/watch?v=2qCH7ek4x9s).
- **Gappy voicings on purpose** — vocal stacks fill the middle (Rya
  https://www.youtube.com/watch?v=O3otuL8k8_Y; OG Chizzy: vocal textures fill dead space,
  "essential part of all of his beats").

## 3. Groove and rhythm

- **Tempo:** felt **~65–95 BPM** cluster (Clouded 65 … Trust 92; Poison 117 outlier);
  Spotify often reports double-time (131–172). Half-time feel dominates.
- **Swing:** applied by feel — "turned up the swing a pretty decent amount… pretty swingy
  hi-hat" (Dylvinci https://www.youtube.com/watch?v=nuCLKj5Sl34). **No source states a
  percentage.** Engine starting band 54–62% = pure INFERENCE, tune by ear. Some adjacent
  cuts fully triplet/6-8.
- **Humanization explicit:** "humanize 10% + randomized velocity" (Kabeh
  https://www.youtube.com/watch?v=7T-yvdlaxG8); **"rush the snap and drag the clap"**
  (Make Pop Music https://www.youtube.com/watch?v=8IXWrB1H_KI).
- **Drum anatomy (CITED across tutorials):** sparse kick ("leaves me space" — B Stix
  https://www.youtube.com/watch?v=5nZh78ZCrKU); backbeat = **soft composite** (rim-as-clap,
  snap+clap+live-flam stacks, snare+snare+clap) — not a hard trap snare; hats **two-step
  with alternating velocities**, occasional short rolls; dense-but-quiet hand-perc beds
  ("seven+ individual percs… fill the pockets"); **tom/bongo turnarounds at phrase ends**
  ("you'll hear this a lot in Brent Faiyaz's music" — OG Chizzy); two alternating drum
  patterns per song, one flowing one choppy, "Timbaland-inspired" (Hix).
- **Trap present but subordinate:** "a lot more spaced out… a lot more low fidelity"
  (VLTN). Era refs: boom-bap-influenced (*Sonder Son*, Pitchfork), late-90s radio R&B
  staggered percussion (*LTL*), new-jack-swing weightlessness (*Icon*).
- **Drums come last — or never.** Brent: "I don't care if I have four, five, six, seven
  tracks that don't have drums on it"; stacks vocals first, "then create the rest of the
  beat around it" (Rolling Stone
  https://www.rollingstone.com/music/music-features/brent-faiyaz-fuck-the-world-rehab-interview-948080/).
  Jordan Waré: "a lot of dead space is great."

## 4. Bass

- **Real(-sounding) bass guitar over 808s — most repeated instruction.** "He almost always
  uses some sort of real sounding bass" (OG Chizzy); "nothing hits like a live bass"
  (VLTN). Named tool ×3 tutorials: **Scarbee Rickenbacker Bass**. Los Hendrix (in-camp):
  "He works off of basslines… and kind of just writes the whole song"
  (https://www.revolt.tv/article/2021-04-15/55687/studio-sessions-loshendrix-on-impressing-sza-with-good-days-and-developing-brent-faiyazs-sound).
- **Layering:** sub + bass guitar together; sub stays on roots, guitar takes passing
  notes (Hix). 808s additive, not foundation.
- **Movement:** melodic call-and-response licks, R&B double-stab, walk-downs;
  root-anchored, ornamented.
- **Glide documented:** synth-bass glide (Rya); the sliding sub on "All Mine" famous
  enough for its own how-to thread
  (https://www.reddit.com/r/makinghiphop/comments/ym6sbw/).
- **Processing:** overdrive/saturation; **mono** ("I want a really nice mono bass" — Make
  Pop Music); sidechain to kick **4–5 dB** (B Stix).

## 5. Sound palette and texture

**Instruments (CITED):** Rhodes/EP everywhere (Waves Electric 88, S.K.Y. Keys, Analog Lab
"Classic Rode"); **strings as the cake, not garnish** (*Wasteland*): Jordan Waré — "what
I'm doing with them is the actual cake," violins through pedals, "tremolo-type… Jordan
Peele type of movie" on DMW
(https://www.okayplayer.com/producer-jordan-ware-is-the-secret-weapon-behind-brent-faiyazs-wasteland/409506);
guitar (Los Hendrix pedals; Steve Lacy on Gravity); **vocal-chop/choir textures as glue**
filling dead space; foley/noise floor (vinyl crackle whole-beat, cassette noise "you just
feel them," sirens/rain/dialogue skits). Dahi's Gravity shelf: Prophet-10, Mellotron,
Jupiter-4 (https://www.soundonsound.com/people/dj-dahi-producing-gravity).

**The hazy/dark recipe (CITED components):**
1. **Pitched/formant-shifted vocal layers under the lead** — the most Brent-specific
   trick, triple-sourced: MAutoPitch formant **−5.28** whole song (BlueNova
   https://www.youtube.com/watch?v=FCO2sjomBUk), AlterBoy formant-down doubles + shifted
   delay throws. Critics hear it: "pitched-down vocals slowed to a sludge" (Pitchfork
   *Wasteland*). Brent: "had him pitch the whole track down, whole different vibe."
2. **Mid-speed pitch correction worn as color:** retune ~10 in key; between fast-PND and
   slow-Kehlani; artifacts kept on close-mic'd intimate vocal.
3. **Saturation/tape/lo-fi on the bus:** RC-20 final glue; Wavesfactory Cassette; Softube
   Tape on master; SoundShifter chosen *because* artifacts sound "vintage and lo-fi";
   Origin downsampling ~9 kHz on elements; **brick-wall LP whole mix ~15–16 kHz**
   (BlueNova, twice).
4. **Reverb: mid-size plates/rooms + filtered delay-into-reverb, not halls:** Valhalla
   VintageVerb recurring; ~2.5 s plate with Abbey-Road HP/LP on return; filtered
   low-feedback delays, delay return into reverb; throws sidechained under the lead. Lead
   sits dry/upfront; the *layers* are wet (INFERRED from chains).
5. **Chorus on vocal stacks** (Fruity Chorus 27%), micro-detune layers a few cents apart.
6. **Movement via ducking/filtering, not new notes:** Gross Beat pulsing, sidechain pulse
   on pads, ShaperBox filter motion, auto-pan textures.

**Width:** lead center/upfront; BGVs wide (±15–30, dubs 100%) behind the lead; bass mono.
No measured stereo analysis of the records exists — numbers would be guesses.

**Mix consistency engine:** from *FTW* (2020) on, recording+mixing = **Itai Schwartz**
in-house ("there is magic in your demo" — https://www.itaimix.com/). *Sonder Son* mixed
Jeff Jackson; *LTL* mastered Ryan Schwabe; *Icon* mastered Mike Dean. One set of ears for
6+ years is itself much of "the sound" (INFERRED, well-grounded).

## 6. Arrangement

- **Loop economics:** 2–8 bar loops, verse = chorus, differentiation by add/mute layers,
  not new chords. Variation devices (CITED): mute-based "quick tension, quick release"
  (drop hats a bar), EQ "phone effect" on hook 2, half-time drops, whole-loop pitch shifts
  (−5 st fake I–V; +3 st outros), tape-stop/slowed intros.
- **Short songs, fragment aesthetic:** *FTW* 10 tracks/26:35 ("Make It Out" 0:31); *LTL*
  avg ~2:36; *Wasteland* 19 tracks with 3 skits; *Icon* normalizes ~3:21.
- **Beat switches / two-part suites signature:** "Price of Fame… frantic beat changes";
  Dpat designed "Sirens" to "go from delicate into something hard." Brent: "Within the
  first couple of seconds, I want them to have no idea where the fuck this gonna go."
- **Space is the arrangement:** drumless/drums-late tracks; strings "reset the mood every
  time drums come too close to a real climax" (Mic); "gloriously languid and
  ultra-minimalist" (Clash).
- **Skits/foley as connective tissue**; *LTL* deliberately mixtape-framed ("producer tags,
  air horns; it's all intentional" — Dpat, Billboard).
- **Heuristics (tutorials):** keep the loop "really empty… sparse" and mumble-test it; "a
  sample is half a beat, a beat is half a song"; voice is the focal point; every sound in
  its own pocket.

## 7. The producers

| Name | Credits | Brings |
|---|---|---|
| **Dpat** | Sonder co-founder; 8/12 *LTL*; most of *Icon* | "I'm a chameleon… reverse engineer anything"; sample-flip engine (Kelis → "Best Time"); minimal production so the writing reads |
| **Atu** | Sonder co-founder; FTW | Soulection roots; deliberately low-profile |
| **Jordan Waré** | The sound of *Wasteland* (DMW, Loose Change, Jackie Brown…) | Classically trained violinist; strings-as-cake, pedals on violins, dead-space doctrine, "Cinematic Simplicity"; Logic |
| **Los Hendrix** | Poison, Talk 2 U, Clouded, Been Away, Trust | Guitar chords+pedals; bassline-first insight ("he'll beatbox a track and top-line over it") |
| **Nascent** | Clouded, Been Away, Trust, Price of Fame, Rolling Stone | Sample-soul DNA; Reason; Keyscape/Mellotron/Memorymoog/Juno (LOW-CONF) |
| **L3gion** | Skyline, FTW, Price of Fame, Jackie Brown | No interviews exist (verified negative) |
| **DJ Dahi** | Gravity (sole) | Melody-first, anti-overproduction: "people need space to see themselves on the record" |
| **Neptunes/Chad Hugo** | Wasting Time; *Icon* tracks | The chromatic-lift chord DNA |
| **No I.D.** | Rehab; Loose Change/Role Model co-prod | Jodeci/Timbaland/Static energy read |
| **Raphael Saadiq** | Loose Change, Ghetto Gatsby, Angel; **exec *Icon*** | "I only give my good shit to Solange, D'Angelo, and now you" |
| **Jake One** | Been Away, Rolling Stone | Behind-the-sample video exists |
| **Jonah Roy** | Forever Yours; drums across *Icon* | The drum-pass specialist in loop-first workflow |
| **The-Dream** | writer: Loose Change, Rolling Stone… | "the finisher" |

**Sample DNA:** Jackie Brown ← Ginuwine/Aaliyah "Final Warning" (Timbaland/Static); Wasting
Time ← Five Americans "Western Union"; Best Time ← Kelis; Trust interpolates Guy "Let's
Chill". Reference universe: **1994–2002 Timbaland/Neptunes/Jodeci R&B.**

## 8. Engine defaults (INFERRED synthesis, grounded above)

- **Harmony:** minor center (Am/Bm/C#m/Dm/Fm/Gm/G#m weighted); 2–4 chord Aeolian loop from
  {i7/i9, v7, ♭VImaj7, iv7/iv6add9, ♭III}; p≈0.3 swap in Dorian ii(m7) or ♭II half-step
  vamp; harmonic-minor V7(♭9/♭13) kicker p≈0.25; close 4–5 note stacks, 7ths/9ths standard,
  mid register, roots to bass; verse = chorus; no modulation except whole-loop transpose
  (±3–5 st) as section event.
- **Groove:** felt 65–95 half-time; composite backbeat on 3 (rim/snap/clap; snap rushed
  −10..−20 ms, clap dragged +10..+20 ms); sparse kick; two-step velocity-alternating hats,
  light swing (54–62% starting band, INFERRED); low-velocity perc bed; tom/bongo phrase
  turnarounds; humanize ~10%.
- **Bass:** bass-guitar timbre root+licks, mono, saturated; sub layer straight roots;
  occasional glide; sidechain 4–5 dB to kick.
- **Texture:** Rhodes/EP + strings/guitar + vocal-chop bed + vinyl/cassette floor; tape
  saturation on bus; brickwall LP ~15 kHz; plate ~2.5 s filtered sends; formant-down (−4
  to −5) doubles and pitched-down throws under dry-ish centered lead; wide BGV stacks.
- **Arrangement:** 2–8 bar loop, 1:30–3:30; sections by mutes/EQ/half-time drops; drumless
  sections allowed; foley/skit bookends.

**Open conflicts to carry as uncertainty:** Rehab key (weight A minor — note-level tools
agree), Jackie Brown's exact loop, Been Away/Talk 2 U key splits, All Mine tempo (71 vs
76), the NDK gear list (single low-authority source). No swing percentages, measured
stereo widths, or *FTW*/*Wasteland* mastering credits exist publicly — true gaps.
