from __future__ import annotations

import supriya


@supriya.synthdef()
def rhodey(
    frequency: float = 220.0,
    amplitude: float = 0.3,
    gate: float = 1.0,
    pan: float = 0.0,
    out: float = 0.0,
) -> None:
    from supriya.ugens import Envelope, EnvGen, Out, Pan2, SinOsc

    index = 0.2 + amplitude * 1.8
    bell_env = EnvGen.kr(envelope=Envelope.percussive(attack_time=0.001, release_time=1.0))
    bell = SinOsc.ar(frequency=frequency * 4.0) * index * bell_env
    tine = SinOsc.ar(frequency=frequency, phase=bell)
    bark_env = EnvGen.kr(envelope=Envelope.percussive(attack_time=0.001, release_time=0.09))
    bark = SinOsc.ar(frequency=frequency * 0.5) * bark_env * amplitude
    body = EnvGen.kr(
        envelope=Envelope.adsr(attack_time=0.002, decay_time=1.2, sustain=0.55, release_time=0.35),
        gate=gate,
        done_action=2,
    )
    signal = (tine * 0.85 + bark * 0.35) * body * amplitude
    Out.ar(bus=out, source=Pan2.ar(source=signal, position=pan))


@supriya.synthdef()
def pad(
    frequency: float = 220.0, amplitude: float = 0.2, gate: float = 1.0, out: float = 0.0
) -> None:
    from supriya.ugens import Envelope, EnvGen, LFSaw, LPF, Out, Pan2

    saws = LFSaw.ar(frequency=frequency) + LFSaw.ar(frequency=frequency + 0.6)
    filtered = LPF.ar(source=saws * 0.5, frequency=frequency * 6.0)
    env = EnvGen.kr(
        envelope=Envelope.adsr(attack_time=0.6, decay_time=0.4, sustain=0.8, release_time=0.9),
        gate=gate,
        done_action=2,
    )
    Out.ar(bus=out, source=Pan2.ar(source=filtered * env * amplitude, position=0.0))


@supriya.synthdef()
def subbass(
    frequency: float = 55.0, amplitude: float = 0.5, gate: float = 1.0, out: float = 0.0
) -> None:
    from supriya.ugens import Envelope, EnvGen, Out, SinOsc

    env = EnvGen.kr(
        envelope=Envelope.adsr(attack_time=0.005, decay_time=0.1, sustain=0.9, release_time=0.12),
        gate=gate,
        done_action=2,
    )
    signal = (SinOsc.ar(frequency=frequency) * 1.8).tanh() * env * amplitude
    Out.ar(bus=out, source=[signal, signal])


@supriya.synthdef()
def bassgtr(
    frequency: float = 110.0,
    amplitude: float = 0.4,
    gate: float = 1.0,
    glide: float = 0.0,
    out: float = 0.0,
) -> None:
    from supriya.ugens import Envelope, EnvGen, Lag, LFPulse, LFSaw, LPF, Out, Pan2

    freq = Lag.kr(source=frequency, lag_time=glide * 0.08)
    raw = LFSaw.ar(frequency=freq) * 0.6 + LFPulse.ar(frequency=freq, width=0.45) * 0.4
    shaped = LPF.ar(source=(raw * 1.4).tanh(), frequency=1400.0)
    env = EnvGen.kr(
        envelope=Envelope.adsr(attack_time=0.004, decay_time=0.35, sustain=0.5, release_time=0.1),
        gate=gate,
        done_action=2,
    )
    Out.ar(bus=out, source=Pan2.ar(source=shaped * env * amplitude, position=0.0))


@supriya.synthdef()
def drum(
    buffer_id: float = 0.0,
    amplitude: float = 0.8,
    rate: float = 1.0,
    pan: float = 0.0,
    out: float = 0.0,
) -> None:
    from supriya.ugens import Out, Pan2, PlayBuf

    signal = PlayBuf.ar(channel_count=1, buffer_id=buffer_id, rate=rate, done_action=2)
    Out.ar(bus=out, source=Pan2.ar(source=signal * amplitude, position=pan))


def compile_all() -> dict[str, bytes]:
    defs = {"rhodey": rhodey, "pad": pad, "subbass": subbass, "bassgtr": bassgtr, "drum": drum}
    return {name: bytes(sd.compile()) for name, sd in defs.items()}
