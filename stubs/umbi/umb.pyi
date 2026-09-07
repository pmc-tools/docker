from pathlib import Path


class TransitionSystem:
    num_states: int
    num_branches: int


class Index:
    transition_system: TransitionSystem


class ExplicitUmb:
    index: Index


def read(path: str | Path, strict: bool = False) -> ExplicitUmb: ...


def write(model: ExplicitUmb, path: str | Path) -> None: ...