from lattice.theory.interval import A4, M3, M7, P5, d5, m3, m7, semitones


def test_interval_semitone_spans() -> None:
    assert semitones(P5) == 7
    assert semitones(M3) == 4
    assert semitones(m3) == 3
    assert semitones(m7) == 10
    assert semitones(M7) == 11


def test_tritone_is_two_different_intervals() -> None:
    assert A4 != d5
    assert semitones(A4) == semitones(d5) == 6
