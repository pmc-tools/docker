import tempfile
from typing import List
from umbtest.tools import UmbTool
from pathlib import Path


class UmbBenchmark:
    def __init__(self, location):
        self._location = location


benchmarks = []


class Tester:
    def __init__(self):
        self._tmpdir = tempfile.TemporaryDirectory()

    def _tmpumbfile(self):
        return tempfile.NamedTemporaryFile(dir=self._tmpdir.name, suffix=".umb")

    def _tmplogfile(self):
        return tempfile.NamedTemporaryFile(dir=self._tmpdir.name, suffix=".log")

    def check_prism_file(self, prism_file: Path, properties: List[str], loader: UmbTool, transformer: None | UmbTool,
                         checker: UmbTool):
        tmpfile_in = self._tmpumbfile()
        log_file_to_umb = self._tmplogfile()
        loader.prism_file_to_umb(prism_file, Path(tmpfile_in.name), log_file=Path(log_file_to_umb.name))
        if transformer:
            tmpfile_out = self._tmpumbfile()
            transformer.umb_to_umb(Path(tmpfile_in.name), Path(tmpfile_out.name),
                                   log_file=Path(self._tmplogfile().name))
        else:
            tmpfile_out = tmpfile_in
        checker.check_umb(Path(tmpfile_out.name), log_file=Path(self._tmplogfile().name), properties=properties)


