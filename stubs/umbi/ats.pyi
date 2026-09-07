from pathlib import Path


class SimpleAts:
    num_states: int
    num_branches: int


def read(path: str | Path, strict: bool = False) -> SimpleAts: ...


def write(model: SimpleAts, path: str | Path) -> None: ...