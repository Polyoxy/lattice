import pytest

from lattice.cards import CONDUCTOR, FAIYAZ, MOLINA, get_card


def test_presets_resolve_by_name() -> None:
    assert get_card("faiyaz") is FAIYAZ
    assert get_card("conductor") is CONDUCTOR
    assert get_card("molina") is MOLINA
    with pytest.raises(KeyError):
        get_card("drake")


def test_faiyaz_documented_values() -> None:
    c = FAIYAZ
    assert c.bpm_range == (65, 95)
    assert c.snap_rush_ms == (-20.0, -10.0)
    assert c.clap_drag_ms == (10.0, 20.0)
    assert c.swing_band == (0.54, 0.62)
    assert not c.allow_tritone_sub
    assert not c.allow_chromatic_mediant
    assert "i7" in c.function_pool and "bII" in c.function_pool
    assert "Imaj7" in c.major_function_pool and "vii_m7" in c.major_function_pool


def test_documented_absences_vs_molina() -> None:
    assert MOLINA.allow_tritone_sub and MOLINA.allow_chromatic_mediant
    assert MOLINA.elaboration_density > FAIYAZ.elaboration_density


def test_conductor_documented_values() -> None:
    c = CONDUCTOR
    assert c.bpm_range == (80, 100)
    assert c.p_drumless == pytest.approx(0.15)
    assert c.ghost_kicks
    assert c.swing_band == (0.5, 0.5)


def test_provenance_flags_swing_as_inferred() -> None:
    prov = dict(FAIYAZ.provenance)
    assert prov["swing_band"] == "inferred"
    assert prov["snap_rush_ms"] == "cited"


def test_override_returns_new_card() -> None:
    c2 = FAIYAZ.override(p_drumless=0.5)
    assert c2.p_drumless == 0.5 and FAIYAZ.p_drumless != 0.5 and c2.name == FAIYAZ.name


def test_bridge_fields_default_empty() -> None:
    from lattice.cards import FAIYAZ

    assert FAIYAZ.has_bridge is False
    assert FAIYAZ.bridge_len_weights == ()


def test_ballroom_card_registered() -> None:
    card = get_card("ballroom")
    assert card.name == "ballroom"
    assert card.p_major_center == 1.0
    assert card.has_bridge and card.section_pattern == "AABA"
    assert card.bass_feel == "two" and card.bridge_bass_feel == "walk"
    assert card.keys_pattern == "stride" and card.has_strings
    assert card.bpm_range == (104, 126)


def test_new_card_fields_default_inert() -> None:
    for name in ("faiyaz", "conductor", "molina", "tunisia"):
        c = get_card(name)
        assert c.section_pattern == "AB" and c.keys_pattern == "comp"
        assert c.bass_feel == "riff" and c.bridge_bass_feel == ""
        assert c.pad_enters_section == 0 and not c.has_strings
