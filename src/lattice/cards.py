from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Final


@dataclass(frozen=True, slots=True)
class StyleCard:
    name: str
    centers: tuple[str, ...]
    p_major_center: float
    major_centers: tuple[str, ...]
    loop_len_weights: tuple[tuple[int, float], ...]
    function_pool: tuple[str, ...]
    major_function_pool: tuple[str, ...]
    p_kicker: float
    p_phrygian_vamp: float
    p_tonic_avoid: float
    allow_tritone_sub: bool
    allow_chromatic_mediant: bool
    elaboration_density: float
    max_changes_per_bar: int
    register_lo: int
    register_hi: int
    rootless: bool
    voicing_density: float
    templates: tuple[str, ...]
    bpm_range: tuple[int, int]
    swing_band: tuple[float, float]
    snap_rush_ms: tuple[float, float]
    clap_drag_ms: tuple[float, float]
    kick_per_bar: tuple[int, int]
    hat_vels: tuple[int, int]
    p_hat_roll: float
    p_perc_bed: float
    p_turnaround: float
    p_drumless: float
    ghost_kicks: bool
    timing_sigma_ms: float
    vel_jitter: float
    p_bass_approach: float
    p_bass_stab: float
    p_bass_glide: float
    p_keys_anticipation: float
    keys_reattack: str
    target_len_s: tuple[int, int]
    p_transpose_event: float
    transpose_semitones: int
    texture: tuple[tuple[str, float], ...]
    provenance: tuple[tuple[str, str], ...]
    has_bridge: bool = False
    bridge_function_pool: tuple[str, ...] = ()
    bridge_major_function_pool: tuple[str, ...] = ()
    bridge_len_weights: tuple[tuple[int, float], ...] = ()
    section_pattern: str = "AB"
    keys_pattern: str = "comp"
    bass_feel: str = "riff"
    bridge_bass_feel: str = ""
    pad_enters_section: int = 0
    has_strings: bool = False
    bridge_keys_pattern: str = ""
    pad_pattern: str = "sustain"
    has_lead: bool = False
    lead_enters_section: int = 0
    motifs: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...] = ()

    def override(self, **kwargs: Any) -> StyleCard:
        return replace(self, **kwargs)


FAIYAZ: Final = StyleCard(
    name="faiyaz",
    centers=("Am", "Bm", "C#m", "Dm", "Fm", "Gm", "G#m"),
    p_major_center=0.2,
    major_centers=("C", "D", "E", "Ab"),
    loop_len_weights=((1, 0.05), (2, 0.35), (3, 0.25), (4, 0.35)),
    function_pool=(
        "i7", "i9", "i6add9", "iv7", "iv9", "iv6add9", "v7", "V7", "V7b9",
        "V7b13", "bVImaj7", "bIII", "bVII9", "ii7", "bII", "IV7",
    ),
    major_function_pool=(
        "Imaj7", "ii9", "ii7maj", "iii7", "IVmaj7", "V7maj", "vi7",
        "vii_m7",
    ),
    p_kicker=0.25,
    p_phrygian_vamp=0.15,
    p_tonic_avoid=0.15,
    allow_tritone_sub=False,
    allow_chromatic_mediant=False,
    elaboration_density=0.1,
    max_changes_per_bar=2,
    register_lo=48,
    register_hi=72,
    rootless=True,
    voicing_density=0.25,
    templates=("close4", "close5"),
    bpm_range=(65, 95),
    swing_band=(0.54, 0.62),
    snap_rush_ms=(-20.0, -10.0),
    clap_drag_ms=(10.0, 20.0),
    kick_per_bar=(1, 3),
    hat_vels=(64, 96),
    p_hat_roll=0.15,
    p_perc_bed=0.7,
    p_turnaround=0.8,
    p_drumless=0.05,
    ghost_kicks=False,
    timing_sigma_ms=4.0,
    vel_jitter=0.08,
    p_bass_approach=0.5,
    p_bass_stab=0.35,
    p_bass_glide=0.15,
    p_keys_anticipation=0.3,
    keys_reattack="sustain",
    target_len_s=(90, 150),
    p_transpose_event=0.2,
    transpose_semitones=3,
    texture=(
        ("lpf_hz", 15500.0), ("crackle_db", -38.0), ("wow_depth", 0.15),
        ("pump_db", 4.5), ("reverb_s", 2.5), ("tape_drive", 0.3),
    ),
    provenance=(
        ("bpm_range", "cited"), ("snap_rush_ms", "cited"),
        ("clap_drag_ms", "cited"), ("swing_band", "inferred"),
        ("kick_per_bar", "cited"), ("function_pool", "cited"),
        ("p_kicker", "gate-only-phase-1"), ("p_phrygian_vamp", "reserved-phase-2"),
        ("p_tonic_avoid", "inferred"), ("allow_tritone_sub", "cited-absence"),
        ("allow_chromatic_mediant", "cited-absence"), ("register", "cited"),
        ("texture", "cited"), ("target_len_s", "cited"),
        ("vel_jitter", "cited"), ("timing_sigma_ms", "inferred"),
    ),
)

CONDUCTOR: Final = StyleCard(
    name="conductor",
    centers=("Am", "Cm", "Dm", "Em", "Fm", "Gm"),
    p_major_center=0.3,
    major_centers=("C", "F", "Bb", "Eb", "Ab"),
    loop_len_weights=((2, 0.4), (3, 0.3), (4, 0.3)),
    function_pool=(
        "i7", "i9", "iv7", "iv9", "v7", "V7", "bVImaj7", "bIII", "bVII7",
        "bVII9",
    ),
    major_function_pool=(
        "Imaj7", "ii7maj", "iii7", "IVmaj7", "V7maj", "vi7", "ii9",
    ),
    p_kicker=0.15,
    p_phrygian_vamp=0.0,
    p_tonic_avoid=0.1,
    allow_tritone_sub=False,
    allow_chromatic_mediant=False,
    elaboration_density=0.05,
    max_changes_per_bar=1,
    register_lo=48,
    register_hi=76,
    rootless=False,
    voicing_density=0.4,
    templates=("close4", "close5", "spread"),
    bpm_range=(80, 100),
    swing_band=(0.5, 0.5),
    snap_rush_ms=(0.0, 0.0),
    clap_drag_ms=(0.0, 0.0),
    kick_per_bar=(1, 2),
    hat_vels=(50, 80),
    p_hat_roll=0.0,
    p_perc_bed=0.2,
    p_turnaround=0.3,
    p_drumless=0.15,
    ghost_kicks=True,
    timing_sigma_ms=6.0,
    vel_jitter=0.1,
    p_bass_approach=0.2,
    p_bass_stab=0.1,
    p_bass_glide=0.0,
    p_keys_anticipation=0.15,
    keys_reattack="chop",
    target_len_s=(90, 150),
    p_transpose_event=0.15,
    transpose_semitones=1,
    texture=(
        ("lpf_hz", 9000.0), ("crackle_db", -30.0), ("wow_depth", 0.5),
        ("pump_db", 6.0), ("reverb_s", 1.2), ("tape_drive", 0.6),
    ),
    provenance=(
        ("bpm_range", "cited"), ("p_drumless", "cited"),
        ("ghost_kicks", "cited"), ("swing_band", "cited-absence"),
        ("kick_per_bar", "cited"), ("texture", "cited"),
        ("timing_sigma_ms", "inferred"), ("function_pool", "inferred"),
        ("keys_reattack", "cited"), ("transpose_semitones", "cited"),
        ("p_kicker", "gate-only-phase-1"), ("p_phrygian_vamp", "reserved-phase-2"),
    ),
)

MOLINA: Final = StyleCard(
    name="molina",
    centers=("Cm", "Fm", "Gm", "Am", "Ebm"),
    p_major_center=0.5,
    major_centers=("C", "F", "G", "Db", "Ab", "Eb"),
    loop_len_weights=((2, 0.2), (3, 0.3), (4, 0.5)),
    function_pool=(
        "i7", "i9", "iv7", "iv9", "v7", "V7", "V7b9", "V7b13", "bVImaj7",
        "bIII", "bVII7", "ii7", "iim7b5", "bII",
    ),
    major_function_pool=(
        "Imaj7", "ii9", "ii7maj", "iii7", "IVmaj7", "V7maj", "vi7",
    ),
    p_kicker=0.6,
    p_phrygian_vamp=0.05,
    p_tonic_avoid=0.05,
    allow_tritone_sub=True,
    allow_chromatic_mediant=True,
    elaboration_density=0.6,
    max_changes_per_bar=4,
    register_lo=43,
    register_hi=79,
    rootless=True,
    voicing_density=0.9,
    templates=(
        "close4", "close5", "drop2", "quartal", "us_triad", "sus43", "add9",
    ),
    bpm_range=(60, 110),
    swing_band=(0.55, 0.66),
    snap_rush_ms=(0.0, 0.0),
    clap_drag_ms=(0.0, 0.0),
    kick_per_bar=(1, 2),
    hat_vels=(40, 70),
    p_hat_roll=0.05,
    p_perc_bed=0.1,
    p_turnaround=0.5,
    p_drumless=0.3,
    ghost_kicks=False,
    timing_sigma_ms=5.0,
    vel_jitter=0.1,
    p_bass_approach=0.6,
    p_bass_stab=0.1,
    p_bass_glide=0.0,
    p_keys_anticipation=0.2,
    keys_reattack="sustain",
    target_len_s=(90, 150),
    p_transpose_event=0.1,
    transpose_semitones=3,
    texture=(
        ("lpf_hz", 18000.0), ("crackle_db", -60.0), ("wow_depth", 0.0),
        ("pump_db", 1.0), ("reverb_s", 1.8), ("tape_drive", 0.15),
    ),
    provenance=(
        ("function_pool", "cited"), ("elaboration_density", "cited"),
        ("allow_tritone_sub", "cited"), ("bpm_range", "inferred"),
        ("templates", "cited"), ("p_kicker", "gate-only-phase-1"),
        ("p_phrygian_vamp", "reserved-phase-2"), ("swing_band", "inferred"),
        ("timing_sigma_ms", "inferred"),
    ),
)

TUNISIA: Final = StyleCard(
    name="tunisia",
    centers=("Dm", "Am", "Em", "Gm", "Cm"),
    p_major_center=0.15,
    major_centers=("F", "C", "Bb", "Eb"),
    loop_len_weights=((2, 0.7), (3, 0.2), (4, 0.1)),
    function_pool=(
        "i7", "i9", "i6add9", "bII", "iv7", "V7b9",
    ),
    major_function_pool=("Imaj7", "ii9", "IVmaj7", "V7maj", "vi7"),
    p_kicker=0.4,
    p_phrygian_vamp=0.6,
    p_tonic_avoid=0.1,
    allow_tritone_sub=True,
    allow_chromatic_mediant=False,
    elaboration_density=0.4,
    max_changes_per_bar=3,
    register_lo=43,
    register_hi=79,
    rootless=True,
    voicing_density=0.7,
    templates=(
        "close4", "close5", "drop2", "quartal", "us_triad", "sus43", "add9",
    ),
    bpm_range=(128, 152),
    swing_band=(0.58, 0.66),
    snap_rush_ms=(0.0, 0.0),
    clap_drag_ms=(0.0, 0.0),
    kick_per_bar=(1, 2),
    hat_vels=(45, 75),
    p_hat_roll=0.05,
    p_perc_bed=0.7,
    p_turnaround=0.6,
    p_drumless=0.1,
    ghost_kicks=False,
    timing_sigma_ms=5.0,
    vel_jitter=0.1,
    p_bass_approach=0.6,
    p_bass_stab=0.2,
    p_bass_glide=0.05,
    p_keys_anticipation=0.25,
    keys_reattack="sustain",
    target_len_s=(90, 150),
    p_transpose_event=0.1,
    transpose_semitones=3,
    texture=(
        ("lpf_hz", 17000.0), ("crackle_db", -55.0), ("wow_depth", 0.05),
        ("pump_db", 1.5), ("reverb_s", 1.6), ("tape_drive", 0.25),
    ),
    provenance=(
        ("all", "designed"), ("p_phrygian_vamp", "reserved-phase-2"),
        ("function_pool", "designed"), ("bridge_function_pool", "designed"),
    ),
    has_bridge=True,
    bridge_function_pool=(
        "iim7b5", "V7b9", "i7", "iv7", "bVII7", "V7b13", "ii7", "v7",
    ),
    bridge_major_function_pool=("ii9", "V7maj", "Imaj7", "IVmaj7", "vi7"),
    bridge_len_weights=((3, 0.5), (4, 0.5)),
)

BALLROOM: Final = StyleCard(
    name="ballroom",
    centers=("Dm",),
    p_major_center=1.0,
    major_centers=("F", "Ab", "Eb", "C"),
    loop_len_weights=((2, 0.35), (4, 0.65)),
    function_pool=("i7", "iv7", "V7"),
    major_function_pool=(
        "I6", "I6add9", "ii7maj", "iii7", "IV6", "iv6", "V7maj", "VI7",
        "vi7", "#idim7", "II7",
    ),
    p_kicker=0.0,
    p_phrygian_vamp=0.0,
    p_tonic_avoid=0.05,
    allow_tritone_sub=False,
    allow_chromatic_mediant=True,
    elaboration_density=0.15,
    max_changes_per_bar=2,
    register_lo=48,
    register_hi=76,
    rootless=False,
    voicing_density=0.5,
    templates=(
        "close4", "close5", "drop2", "quartal", "us_triad", "sus43", "add9",
    ),
    bpm_range=(104, 126),
    swing_band=(0.58, 0.68),
    snap_rush_ms=(6.0, 14.0),
    clap_drag_ms=(0.0, 0.0),
    kick_per_bar=(1, 1),
    hat_vels=(38, 52),
    p_hat_roll=0.0,
    p_perc_bed=0.0,
    p_turnaround=0.0,
    p_drumless=0.0,
    ghost_kicks=False,
    timing_sigma_ms=3.5,
    vel_jitter=0.05,
    p_bass_approach=0.0,
    p_bass_stab=0.0,
    p_bass_glide=0.0,
    p_keys_anticipation=0.12,
    keys_reattack="sustain",
    target_len_s=(150, 210),
    p_transpose_event=0.0,
    transpose_semitones=0,
    texture=(
        ("lpf_hz", 14000.0), ("room_size", 0.85), ("verb_mix", 0.24),
        ("glue_db", 3.0),
    ),
    provenance=(
        ("bpm_range", "cited: ISTD slow foxtrot 112-120 inside band; ballroom-dna 7"),
        (
            "swing_band",
            "designed: dance-band charts straighter than combo 0.70-0.76; ballroom-dna 1",
        ),
        (
            "snap_rush_ms",
            "designed: brush drag behind the beat; ballroom-dna 2 contested direction",
        ),
        ("major_function_pool", "cited: added-sixth tonic, Martin 2023; ballroom-dna 6"),
        ("section_pattern", "cited: 32-bar AABA dominance; ballroom-dna 6"),
        ("texture", "designed: warm ceiling, big room, no lo-fi"),
    ),
    has_bridge=True,
    bridge_function_pool=("i7", "iv7", "V7"),
    bridge_major_function_pool=(
        "III7", "VI7", "II7", "V7maj", "V9", "iii7", "vi7", "ii7maj",
    ),
    bridge_len_weights=((2, 0.5), (4, 0.5)),
    section_pattern="AABA",
    keys_pattern="stride",
    bass_feel="two",
    bridge_bass_feel="walk",
    pad_enters_section=2,
    has_strings=True,
)

CHASE: Final = StyleCard(
    name="chase",
    centers=("Dm", "Gm", "Cm", "Fm"),
    p_major_center=0.0,
    major_centers=("C",),
    loop_len_weights=((2, 0.3), (4, 0.7)),
    function_pool=(
        "i7", "i9", "iv7", "iv9", "bVII7", "bVImaj7", "V7", "V7b9", "v7", "iim7b5",
    ),
    major_function_pool=(
        "Imaj7", "ii7maj", "iii7", "IVmaj7", "V7maj", "vi7", "ii9",
    ),
    p_kicker=0.0,
    p_phrygian_vamp=0.0,
    p_tonic_avoid=0.1,
    allow_tritone_sub=False,
    allow_chromatic_mediant=True,
    elaboration_density=0.12,
    max_changes_per_bar=2,
    register_lo=50,
    register_hi=74,
    rootless=False,
    voicing_density=0.5,
    templates=(
        "close4", "close5", "drop2", "quartal", "us_triad", "sus43", "add9",
    ),
    bpm_range=(150, 170),
    swing_band=(0.5, 0.5),
    snap_rush_ms=(0.0, 0.0),
    clap_drag_ms=(0.0, 0.0),
    kick_per_bar=(1, 2),
    hat_vels=(42, 60),
    p_hat_roll=0.0,
    p_perc_bed=0.0,
    p_turnaround=0.0,
    p_drumless=0.0,
    ghost_kicks=False,
    timing_sigma_ms=2.5,
    vel_jitter=0.06,
    p_bass_approach=0.2,
    p_bass_stab=0.15,
    p_bass_glide=0.3,
    p_keys_anticipation=0.0,
    keys_reattack="sustain",
    target_len_s=(180, 225),
    p_transpose_event=0.0,
    transpose_semitones=0,
    texture=(
        ("lpf_hz", 16000.0), ("room_size", 0.35), ("verb_mix", 0.12), ("glue_db", 2.0),
    ),
    provenance=(
        ("bpm_range", "designed: highway pulse"),
        ("swing_band", "designed: dead straight, the road doesn't swing"),
        ("motifs", "designed"),
        ("section_pattern", "designed: the solo needs a home"),
        (
            "card_idioms",
            "cited: descending-tetrachord lament figure; designed weights",
        ),
        (
            "snap_rush_ms",
            "designed: dead-straight rim, not dragged; supersedes spec table's "
            "(-4.0, 0.0), corrected in task 11",
        ),
    ),
    has_bridge=True,
    bridge_function_pool=("i7", "iv9", "bVImaj7", "V7b9", "iim7b5", "bVII7"),
    bridge_major_function_pool=(
        "Imaj7", "ii7maj", "iii7", "IVmaj7", "V7maj", "vi7", "ii9",
    ),
    bridge_len_weights=((2, 0.5), (4, 0.5)),
    section_pattern="AABA",
    keys_pattern="duel",
    bass_feel="riff",
    pad_enters_section=2,
    has_strings=True,
    bridge_keys_pattern="duel_low",
    pad_pattern="answer",
    has_lead=True,
    lead_enters_section=3,
    motifs=(
        # sigh, cry, spiral, push, defiance
        ((-3, 0), (0, 2)),
        ((1, -4, 1), (0, 1, 2)),
        ((0, -2, -4, 1), (0, 1, 2, 3)),
        ((0, 0, 0), (0, 1, 3)),
        ((1, -2, 0), (0, 2, 3)),
    ),
)

_CARDS: Final = {c.name: c for c in (FAIYAZ, CONDUCTOR, MOLINA, TUNISIA, BALLROOM, CHASE)}


def get_card(name: str) -> StyleCard:
    return _CARDS[name]
