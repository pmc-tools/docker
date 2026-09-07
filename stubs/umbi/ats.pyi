from pathlib import Path


class SimpleAts:
    num_states: int
    num_branches: int


def read(path: Path) -> SimpleAts: ...


def write(model: SimpleAts, path: Path) -> None: ...