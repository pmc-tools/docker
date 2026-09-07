from pathlib import Path

import pytest

from umbtest.benchmarks import Tester
from umbtest.tools import (
    ModestCLI,
    PrismCLI,
    StormCLI,
    UmbPython,
    UmbTool,
    configure_umbtools,
)

RESOURCE = Path(__file__).parent.parent / "resources" / "prism-files" / "tiny_rewards2.nm"


def _available(tool: UmbTool) -> bool:
    try:
        return bool(tool.check_process())
    except Exception:
        return False


@pytest.fixture(scope="session")
def prism_cli() -> PrismCLI:
    try:
        configure_umbtools()
    except FileNotFoundError:
        pytest.skip("No tools.toml found (configure tool paths first).")
    cli = PrismCLI(custom_identifier="Prism")
    if not _available(cli):
        pytest.skip("Prism executable not available.")
    return cli


@pytest.fixture(scope="session")
def modest_cli() -> ModestCLI:
    cli = ModestCLI(custom_identifier="Modest")
    if not _available(cli):
        pytest.skip("Modest executable not available.")
    return cli


@pytest.fixture(scope="session")
def storm_cli() -> StormCLI:
    cli = StormCLI(custom_identifier="Storm")
    if not _available(cli):
        pytest.skip("Storm executable not available.")
    return cli


def test_prism_roundtrip(prism_cli: PrismCLI) -> None:
    tester = Tester()
    tester.set_chain(loader=prism_cli, checker=prism_cli)
    results = tester.check_prism_file(RESOURCE, [])
    assert results["loader"].exit_code == 0
    assert results["checker"].exit_code == 0
    info = results["loader"].model_info
    assert info is not None
    assert info["states"] == 4


def test_prism_roundtrip_via_umbi(prism_cli: PrismCLI) -> None:
    tester = Tester()
    tester.set_chain(loader=prism_cli, transformer=UmbPython("umb"), checker=prism_cli)
    results = tester.check_prism_file(RESOURCE, [])
    assert results["loader"].exit_code == 0
    assert results["transformer"] is not None
    assert results["transformer"].exit_code == 0
    assert results["checker"].exit_code == 0


def test_prism_loader_modest_checker(
    prism_cli: PrismCLI, modest_cli: ModestCLI
) -> None:
    tester = Tester()
    tester.set_chain(loader=prism_cli, checker=modest_cli)
    results = tester.check_prism_file(RESOURCE, [])
    assert results["loader"].exit_code == 0