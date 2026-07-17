from __future__ import annotations

from pathlib import Path

import supriya


@supriya.synthdef()
def _sine(frequency: float = 440.0, amplitude: float = 0.2) -> None:
    from supriya.ugens import Envelope, EnvGen, Out, SinOsc

    envelope = EnvGen.kr(
        envelope=Envelope.linen(attack_time=0.01, sustain_time=0.95, release_time=0.03),
        done_action=2,
    )
    signal = SinOsc.ar(frequency=frequency) * amplitude * envelope
    Out.ar(bus=0, source=[signal, signal])


def render_sine(path: str, seconds: float, frequency: float) -> None:
    score = supriya.Score(output_bus_channel_count=2)
    with score.at(0):
        score.add_synthdefs(_sine)
        score.add_synth(_sine, frequency=frequency)
    output_file_path, exit_code = supriya.render(
        score,
        output_file_path=Path(path),
        duration=seconds,
        sample_rate=44100,
        header_format="wav",
    )
    if exit_code != 0 or output_file_path is None:
        raise RuntimeError(f"scsynth NRT render failed with exit code {exit_code}")
