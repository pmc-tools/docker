from pathlib import Path


class TransitionSystem:
    num_states: int
    num_branches: int


class Index:
    transition_system: TransitionSystem


class ExplicitUmb:
    index: Index


def read(path: Path) -> ExplicitUmb: ...


def write(model: ExplicitUmb, path: Path) -> None: ...