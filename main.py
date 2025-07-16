from pathlib import Path
from umbtest.benchmarks import Tester
from umbtest.tools import PrismCLI, StormCLI, UmbPython

tester = Tester()
#tester.check_prism_file(Path("/opt/prism/prism-examples/simple/dice/dice.pm"), ["R=? [F d=7]"], PrismCLI, PrismCLI, PrismCLI)
tester.check_prism_file(Path("/opt/prism/prism-examples/simple/dice/dice.pm"), ["R=? [F d=7]"], PrismCLI, PrismCLI, PrismCLI)
