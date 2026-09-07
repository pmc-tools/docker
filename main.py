from pathlib import Path
from umbtest.benchmarks import Tester
from umbtest.config import load_config
from umbtest.tools import PrismCLI, StormCLI, UmbPython, check_tools, configure_umbtools

configure_umbtools()
prism_cli = PrismCLI()
storm_cli = StormCLI()
umb_py = UmbPython()
check_tools(prism_cli, storm_cli, umb_py)

byproducts = load_config()["byproducts"]
tester = Tester(
    testdir=byproducts.get("tmpfolder"),
    delete_files=bool(byproducts.get("cleanup", True)),
)
tester.set_chain(prism_cli, umb_py, storm_cli)

tester.check_prism_file(
    Path(prism_cli.prism_dir_path) / "prism-examples/simple/dice/dice.pm",
    ["R=? [F d=7]"],
)
