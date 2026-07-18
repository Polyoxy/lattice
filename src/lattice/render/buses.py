from __future__ import annotations

from typing import Final, cast

import supriya
from supriya.ugens.core import UGenOperable, UGenVector

_FAIYAZ_RAND_ID: Final = 1
_CONDUCTOR_RAND_ID: Final = 2
_NOISE_SEED: Final = 56173.0
_CRACKLE_DENSITY: Final = 140.0
_CRACKLE_FREQ: Final = 2600.0
_CRACKLE_RQ: Final = 0.9


def _pump_slope(pump_db: float, reference_db: float, reference_slope: float) -> float:
    reference_duck = 1.0 - reference_slope
    # card overrides can push pump_db high enough to drive the linear
    # extrapolation negative, which is not a meaningful compander slope
    return max(1.0 - reference_duck * (pump_db / reference_db), 0.05)


def _channels(source: UGenOperable) -> tuple[UGenOperable, UGenOperable]:
    vector = cast(UGenVector, source)
    return vector[0], vector[1]


@supriya.synthdef()
def faiyaz_bus(
    in_bus: float = 0.0,
    kick_bus: float = 0.0,
    out: float = 0.0,
    lpf_hz: float = 15500.0,
    crackle_amp: float = 0.012,
    pump_db: float = 4.5,
    verb_mix: float = 0.22,
) -> None:
    from supriya.ugens import (
        BPF,
        Compander,
        Dust2,
        FreeVerb,
        Impulse,
        In,
        LPF,
        Out,
        RandID,
        RandSeed,
    )

    sig = In.ar(bus=in_bus, channel_count=2)
    kick_left, kick_right = _channels(In.ar(bus=kick_bus, channel_count=2))
    kick_sum = kick_left + kick_right
    ducked = Compander.ar(
        source=sig,
        control=kick_sum,
        threshold=0.25,
        slope_below=1.0,
        slope_above=_pump_slope(pump_db, 4.5, 1.0 / 2.2),
        clamp_time=0.004,
        relax_time=0.18,
    )
    shaped = (ducked * 1.35).tanh()
    filtered = LPF.ar(source=shaped, frequency=lpf_hz)
    verb = FreeVerb.ar(source=filtered, mix=verb_mix, room_size=0.72, damping=0.45)
    RandID.ir(rand_id=_FAIYAZ_RAND_ID)
    RandSeed.ir(seed=_NOISE_SEED, trigger=Impulse.ar(frequency=0))
    crackle = BPF.ar(
        source=Dust2.ar(density=_CRACKLE_DENSITY) * crackle_amp,
        frequency=_CRACKLE_FREQ,
        reciprocal_of_q=_CRACKLE_RQ,
    )
    Out.ar(bus=out, source=verb + crackle)


@supriya.synthdef()
def conductor_bus(
    in_bus: float = 0.0,
    out: float = 0.0,
    sr_hz: float = 11025.0,
    wow_depth: float = 0.5,
    pump_db: float = 6.0,
    lpf_hz: float = 9000.0,
) -> None:
    from supriya.ugens import (
        BPF,
        Compander,
        DelayC,
        Dust2,
        Impulse,
        In,
        Latch,
        LFNoise1,
        LPF,
        Out,
        RandID,
        RandSeed,
        SinOsc,
    )

    RandID.ir(rand_id=_CONDUCTOR_RAND_ID)
    RandSeed.ir(seed=_NOISE_SEED, trigger=Impulse.ar(frequency=0))
    sig = In.ar(bus=in_bus, channel_count=2)
    crushed = Latch.ar(source=sig, trigger=Impulse.ar(frequency=sr_hz))
    wow = SinOsc.kr(frequency=0.5).scale(-1.0, 1.0, 0.0, 0.004 * wow_depth)
    flutter = LFNoise1.kr(frequency=3.0).scale(-1.0, 1.0, 0.0, 0.0015 * wow_depth)
    wowed = DelayC.ar(source=crushed, maximum_delay_time=0.03, delay_time=0.010 + wow + flutter)
    pumped = Compander.ar(
        source=wowed,
        control=wowed,
        threshold=0.2,
        slope_above=_pump_slope(pump_db, 6.0, 1.0 / 2.8),
        clamp_time=0.002,
        relax_time=0.3,
    )
    shaped = (pumped * 1.6).tanh()
    filtered = LPF.ar(source=shaped, frequency=lpf_hz)
    crackle = BPF.ar(
        source=Dust2.ar(density=_CRACKLE_DENSITY) * 0.03,
        frequency=_CRACKLE_FREQ,
        reciprocal_of_q=_CRACKLE_RQ,
    )
    Out.ar(bus=out, source=filtered + crackle)


@supriya.synthdef()
def molina_bus(
    in_bus: float = 0.0,
    out: float = 0.0,
    verb_mix: float = 0.18,
    lpf_hz: float = 18000.0,
) -> None:
    from supriya.ugens import FreeVerb, In, LPF, Out

    sig = In.ar(bus=in_bus, channel_count=2)
    shaped = (sig * 1.1).tanh()
    filtered = LPF.ar(source=shaped, frequency=lpf_hz)
    verb = FreeVerb.ar(source=filtered, mix=verb_mix, room_size=0.6, damping=0.5)
    Out.ar(bus=out, source=verb)


@supriya.synthdef()
def ballroom_bus(
    in_bus: float = 0.0,
    out: float = 0.0,
    lpf_hz: float = 14000.0,
    room_size: float = 0.85,
    verb_mix: float = 0.24,
    glue_db: float = 3.0,
) -> None:
    from supriya.ugens import Compander, FreeVerb, In, LPF, Out

    sig = In.ar(bus=in_bus, channel_count=2)
    glued = Compander.ar(
        source=sig,
        control=sig,
        threshold=0.3,
        slope_above=_pump_slope(glue_db, 3.0, 1.0 / 1.6),
        clamp_time=0.008,
        relax_time=0.25,
    )
    filtered = LPF.ar(source=glued, frequency=lpf_hz)
    verb = FreeVerb.ar(source=filtered, mix=verb_mix, room_size=room_size, damping=0.4)
    Out.ar(bus=out, source=verb)


@supriya.synthdef()
def chase_bus(
    in_bus: float = 0.0,
    out: float = 0.0,
    lpf_hz: float = 16000.0,
    room_size: float = 0.35,
    verb_mix: float = 0.12,
    glue_db: float = 2.0,
) -> None:
    from supriya.ugens import Compander, FreeVerb, In, LPF, Out

    sig = In.ar(bus=in_bus, channel_count=2)
    glued = Compander.ar(
        source=sig,
        control=sig,
        threshold=0.3,
        slope_above=_pump_slope(glue_db, 2.0, 1.0 / 1.6),
        clamp_time=0.008,
        relax_time=0.25,
    )
    filtered = LPF.ar(source=glued, frequency=lpf_hz)
    verb = FreeVerb.ar(source=filtered, mix=verb_mix, room_size=room_size, damping=0.5)
    Out.ar(bus=out, source=verb)


@supriya.synthdef()
def stem_player(
    buffer_id: float = 0.0,
    out: float = 0.0,
    gain: float = 1.0,
    pan: float = 0.0,
    mono: float = 0.0,
) -> None:
    from supriya.ugens import DiskIn, Out

    left, right = _channels(DiskIn.ar(buffer_id=buffer_id, channel_count=2, loop=0))
    mono_sum = (left + right) * 0.5
    source_left = left * (1.0 - mono) + mono_sum * mono
    source_right = right * (1.0 - mono) + mono_sum * mono
    left_gain = 1.0 - (pan + abs(pan)) * 0.5
    right_gain = 1.0 + (pan - abs(pan)) * 0.5
    Out.ar(
        bus=out,
        source=[source_left * left_gain * gain, source_right * right_gain * gain],
    )


@supriya.synthdef()
def master_out(in_bus: float = 0.0, out: float = 0.0, lpf_hz: float = 18000.0) -> None:
    from supriya.ugens import In, Limiter, LPF, Out

    sig = In.ar(bus=in_bus, channel_count=2)
    capped = LPF.ar(source=sig, frequency=lpf_hz)
    capped = LPF.ar(source=capped, frequency=lpf_hz)
    limited = Limiter.ar(source=capped, level=0.95, duration=0.01)
    Out.ar(bus=out, source=limited)


def compile_buses() -> dict[str, bytes]:
    defs = {
        "faiyaz_bus": faiyaz_bus,
        "conductor_bus": conductor_bus,
        "molina_bus": molina_bus,
        "ballroom_bus": ballroom_bus,
        "chase_bus": chase_bus,
        "stem_player": stem_player,
        "master_out": master_out,
    }
    return {name: bytes(sd.compile()) for name, sd in defs.items()}
