from pathlib import Path
from umbtest.benchmarks import Tester
from umbtest.tools import PrismCLI, StormCLI, UmbPython, check_tools

# Note. The following can be used to configure the locations of the tools.
# PrismCLI.prism_dir_path = /path_to_prism_dir/
# StormCLI._storm_path = /path_to_storm_binary
check_tools(PrismCLI, StormCLI, UmbPython)


tester = Tester()
tester.set_chain(PrismCLI, UmbPython, StormCLI)

tester.check_prism_file(
    Path(PrismCLI.prism_dir_path) / "prism-examples/simple/dice/dice.pm",
    ["R=? [F d=7]"],
)
