import pytest
import umbtest.tools

# umbtest.tools.configure_umbtools(
#    "/Users/junges/prism-umb/", "/Users/junges/storm-umb/build/bin/storm"
# )

from umbtest.benchmarks import Tester

toolchains_for_checking = []
for l in [umbtest.tools.PrismCLI, umbtest.tools.StormCLI]:
    for c in [umbtest.tools.PrismCLI, umbtest.tools.StormCLI]:
        for t in [None]:
            toolchain = Tester()
            toolchain.set_chain(loader=l, transformer=t, checker=c)
            toolchains_for_checking.append(toolchain)


@pytest.mark.parametrize("tester", toolchains_for_checking)
@pytest.mark.parametrize("benchmark", umbtest.benchmarks.prism_files)
def test_load_and_read(tester, benchmark):
    print(f"Testing {tester} on {benchmark}...")
    results = tester.check_benchmark(benchmark)
    if results["loader"].anticipated_error:
        pytest.skip("Loader failed with an anticipated error")
    if results["checker"].anticipated_error:
        pytest.skip("Checker failed with an anticipated error")
    assert results["loader"].error_code == 0
    assert results["checker"].error_code == 0
    assert (
        results["loader"].model_info["states"]
        == results["checker"].model_info["states"]
    )
    assert (
        results["loader"].model_info["transitions"]
        == results["checker"].model_info["transitions"]
    )
