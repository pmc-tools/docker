import tempfile
from typing import List
from umbtest.tools import UmbTool, ReportedResults
from pathlib import Path


class UmbBenchmark:
    def __init__(self, location):
        self._location = location


benchmarks = []


class Tester:
    def __init__(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._loader = None
        self._checker = None
        self._transformer = None

    def _tmpumbfile(self):
        return tempfile.NamedTemporaryFile(dir=self._tmpdir.name, suffix=".umb")

    def _tmplogfile(self):
        return tempfile.NamedTemporaryFile(dir=self._tmpdir.name, suffix=".log")

    def set_chain(
        self, loader: UmbTool, transformer: None | UmbTool, checker: UmbTool
    ) -> None:
        self._loader = loader
        self._transformer = transformer
        self._checker = checker

    def check_prism_file(
        self, prism_file: Path, properties: List[str]
    ) -> dict[str, ReportedResults]:
        result = dict()
        if self._loader is None or self._checker is None:
            raise RuntimeError("You must first set the tool chain, using set_chain()")
        tmpfile_in = self._tmpumbfile()
        log_file_to_umb = self._tmplogfile()
        result["loader"] = self._loader.prism_file_to_umb(
            prism_file, Path(tmpfile_in.name), log_file=Path(log_file_to_umb.name)
        )
        if result1.error_code != 0:
            with open(result1.logfile, "r") as f:
                print(f.read())

        if self._transformer:
            tmpfile_out = self._tmpumbfile()
            result["transformer"] = self._transformer.umb_to_umb(
                Path(tmpfile_in.name),
                Path(tmpfile_out.name),
                log_file=Path(self._tmplogfile().name),
            )
        else:
            tmpfile_out = tmpfile_in
        result["checker"] = self._checker.check_umb(
            Path(tmpfile_out.name),
            log_file=Path(self._tmplogfile().name),
            properties=properties,
        )
        return result
