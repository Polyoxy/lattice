from lattice.render.buses import compile_buses


def test_bus_synthdefs_compile() -> None:
    compiled = compile_buses()
    assert set(compiled) >= {"faiyaz_bus", "conductor_bus", "molina_bus", "stem_player"}
    assert all(len(b) > 100 for b in compiled.values())
