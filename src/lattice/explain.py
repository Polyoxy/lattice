from __future__ import annotations

from typing import TYPE_CHECKING

from lattice.theory.chord import symbol
from lattice.theory.key import key_name

if TYPE_CHECKING:
    from lattice.beat import Beat


def explain_beat(beat: Beat) -> str:
    lines: list[str] = []
    bpm_bit = f"{beat.bpm} bpm felt half-time" if beat.card.name == "faiyaz" else f"{beat.bpm} bpm"
    lines.append(
        f"{beat.card.name} · {key_name(beat.key)} · {bpm_bit} · "
        f"{beat.bars}-bar loop · seed {beat.seed}"
    )
    loop_bits = [f"{symbol(fc.chord)} ({fc.roman})" for fc in beat.loop.items]
    lines.append("loop: " + " → ".join(loop_bits))

    loop_romans = {fc.roman for fc in beat.loop.items}
    inserted = [s for s in beat.segments if s.label not in loop_romans]
    if inserted:
        for s in inserted:
            lines.append(f"elaboration: + {symbol(s.chord)} ({s.label}) at slot {s.start_slot}")
    else:
        lines.append("elaboration: none")

    all_pitches = [p for v in beat.voicings for p in v]
    lo = min(all_pitches, key=lambda p: p.midi)
    hi = max(all_pitches, key=lambda p: p.midi)
    tops = [max(v, key=lambda p: p.midi).name() for v in beat.voicings]
    root_note = "rootless" if beat.card.rootless else "rooted"
    lines.append(f"voicing: {root_note}, {lo.name()}–{hi.name()}, top voice {' '.join(tops)}")

    prov = dict(beat.card.provenance)
    swing_flag = " (inferred)" if prov.get("swing_band") == "inferred" else ""
    p = beat.pocket
    lines.append(
        f"groove: swing {p.swing:.2f}{swing_flag} · snap {p.snap_ms:+.0f} ms · "
        f"clap {p.clap_ms:+.0f} ms · jitter σ {p.sigma_ms:.0f} ms"
    )

    arr_bits = []
    for section in beat.timeline.sections:
        bit = f"{section.kind} ×{section.cycles}" if section.cycles > 1 else section.kind
        if section.transpose:
            bit += f" (+{section.transpose} st)"
        arr_bits.append(bit)
    lines.append("arrangement: " + " → ".join(arr_bits))

    tex_bits = [f"{k.replace('_', ' ')} {v:g}" for k, v in beat.card.texture]
    lines.append("texture (render plan): " + " · ".join(tex_bits))
    return "\n".join(lines)
