from pathlib import Path
from umbtest.benchmarks import Tester
from umbtest.tools import PrismCLI, StormCLI, UmbPython, check_tools, configure_umbtools

configure_umbtools()
prism_cli = PrismCLI()
storm_cli = StormCLI()
umb_py = UmbPython()
check_tools(prism_cli, storm_cli, umb_py)

tester = Tester()
tester.set_chain(prism_cli, umb_py, storm_cli)

tester.check_prism_file(
    Path(PrismCLI.prism_dir_path) / "prism-examples/simple/dice/dice.pm",
    ["R=? [F d=7]"],
)
