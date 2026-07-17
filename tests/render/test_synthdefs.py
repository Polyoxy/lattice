from lattice.render.synthdefs import compile_all


def test_all_instrument_synthdefs_compile() -> None:
    compiled = compile_all()
    assert set(compiled) >= {"rhodey", "pad", "subbass", "bassgtr", "drum"}
    assert all(isinstance(b, bytes) and len(b) > 100 for b in compiled.values())
