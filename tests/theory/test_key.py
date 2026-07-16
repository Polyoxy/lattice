from lattice.theory.key import Mode, key_name, parse_key
from lattice.theory.pitch import parse_tpc


def test_parse_minor_and_major() -> None:
    k = parse_key("C#m")
    assert (k.tonic, k.mode) == (parse_tpc("C#"), Mode.AEOLIAN)
    assert parse_key("D").mode == Mode.MAJOR
    assert key_name(parse_key("Gm")) == "Gm"
    assert key_name(parse_key("Ab")) == "Ab"
