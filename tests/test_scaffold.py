from importlib import metadata

import lattice


def test_version() -> None:
    assert lattice.__version__ == metadata.version("lattice")
