from lattice.model import DrumSound, Event
from lattice.render.timing import to_notes


def test_onset_includes_micro_and_clamps_at_zero() -> None:
    mpt = 60000 / (72 * 960)
    events = (
        Event(tick=960, dur=480, vel=127, pitch=69, micro_ms=10.0),
        Event(tick=0, dur=480, vel=64, pitch=60, micro_ms=-50.0),
    )
    notes = to_notes(events, bpm=72)
    assert notes[0].onset_s == 0.0
    assert abs(notes[1].onset_s - (960 * mpt + 10.0) / 1000) < 1e-9
    assert abs(notes[1].freq - 440.0) < 1e-9
    assert notes[1].amp == 1.0


def test_drum_events_carry_drum_not_freq() -> None:
    notes = to_notes((Event(0, 120, 100, drum=DrumSound.KICK),), bpm=90)
    assert notes[0].drum is DrumSound.KICK and notes[0].freq is None


def test_notes_sorted_by_onset() -> None:
    events = (
        Event(tick=480, dur=120, vel=90, drum=DrumSound.SNARE, micro_ms=-400.0),
        Event(tick=0, dur=120, vel=90, drum=DrumSound.KICK, micro_ms=0.0),
    )
    notes = to_notes(events, bpm=60)
    assert notes[0].onset_s <= notes[1].onset_s
