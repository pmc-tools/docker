import pytest
import umbtest.tools
from umbtest.benchmarks import UmbBenchmark, Tester
from umbtest.tools import check_tools

"""
We initialize the tools we use in the tests. 
This can also be used to override the standard paths loaded by the configure tools call.
"""
umbtest.tools.configure_umbtools()
storm_cli = umbtest.tools.StormCLI()
prism_cli = umbtest.tools.PrismCLI()
umbi_py = umbtest.tools.UmbPython()
check_tools(prism_cli, storm_cli)

"""
We define the crosschecks between tools.
"""
crosschecks = []
for l in [prism_cli, storm_cli]:
    for c in [prism_cli, storm_cli]:
        if l==c:
            continue
        for t in [umbtest.tools.UmbPython]:
            toolchain = Tester()
            toolchain.set_chain(loader=l, transformer=t, checker=c)
            crosschecks.append(toolchain)


def _toolname(val: umbtest.tools.UmbTool) -> str:
    """
    Helper function to provide better test names.
    :param val:
    :return:
    """
    return str(val.name)

def _testername(val: Tester) -> str:
    """
    Helper function to provide better test names.
    :param val:
    :return:
    """
    return str(val.id)

def _benchmarkname(val: UmbBenchmark) -> str:
    """
    Helper function to provide better test names.s
    :param val:
    :return:
    """
    return str(val.id)


def load_and_read(tester, benchmark):
    """
    Tests a tool chain.

    :param tester:
    :param benchmark:
    :return:
    """
    print(f"Testing {tester} on {benchmark}...")
    results = tester.check_benchmark(benchmark)
    if results["loader"].anticipated_error:
        pytest.skip("Loader failed with an anticipated error")
    assert results["loader"].error_code == 0
    if results["checker"].anticipated_error:
        pytest.skip("Checker failed with an anticipated error")
    assert results["checker"].error_code == 0
    assert (
        results["loader"].model_info["states"]
        == results["checker"].model_info["states"]
    )
    assert (
        results["loader"].model_info["transitions"]
        == results["checker"].model_info["transitions"]
    )

tools = [storm_cli, prism_cli]
@pytest.mark.parametrize("tool", tools, ids=_toolname, scope="class")
class TestTool:
    @pytest.mark.parametrize(
        "benchmark", umbtest.benchmarks.prism_files, ids=_benchmarkname
    )
    def test_write_read(self, tool, benchmark):
        tester = Tester()
        tester.set_chain(loader=tool, checker=tool)
        load_and_read(tester, benchmark)

    @pytest.mark.parametrize(
        "benchmark", umbtest.benchmarks.prism_files, ids=_benchmarkname
    )
    def test_write_umbi_read(self, tool, benchmark):
        tester = Tester()
        tester.set_chain(loader=tool, transformer=umbi_py, checker=tool)
        load_and_read(tester, benchmark)
