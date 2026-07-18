from lattice.render.buses import compile_buses


def test_bus_synthdefs_compile() -> None:
    compiled = compile_buses()
    assert set(compiled) >= {"faiyaz_bus", "conductor_bus", "molina_bus", "stem_player"}
    assert all(len(b) > 100 for b in compiled.values())


def test_ballroom_bus_compiles() -> None:
    compiled = compile_buses()
    assert "ballroom_bus" in compiled
    assert len(compiled["ballroom_bus"]) > 0


def test_chase_bus_compiles() -> None:
    compiled = compile_buses()
    assert "chase_bus" in compiled
    assert len(compiled["chase_bus"]) > 0
