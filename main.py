from pathlib import Path
from umbtest.benchmarks import Tester
from umbtest.tools import PrismCLI, StormCLI, UmbPython

# Note. The following can be used to configure the locations of the tools.
# PrismCLI.prism_dir_path = "/Users/junges/prism-umb/"
# StormCLI._storm_path = "/Users/junges/storm-umb/build/bin/storm"

tester = Tester()

tester.check_prism_file(Path(PrismCLI.prism_dir_path) / "prism-examples/simple/dice/dice.pm", ["R=? [F d=7]"])
