import subprocess
import pathlib

import logging

logger = logging.getLogger(__name__)


class UmbTool:
    pass


def check_tools(*args):
    for tool in args:
        if not tool.check_process():
            raise RuntimeError(f"Tool '{tool.name}' failed")


class ReportedResults:
    def __init__(self):
        self.timeout = None
        self.memout = None
        self.not_supported = (
            False  # Error messages that say something is not supported.
        )
        self.anticipated_error = (
            False  # Can be used to declare an error message that "makes sense"
        )
        self.error_code = None
        self.model_info = None
        self.logfile = None

    def __str__(self):
        return f"ReportedResults[{self.logfile},{self.error_code},{self.model_info},{self.timeout},{self.memout}]"


class PrismCLI(UmbTool):
    prism_dir_path = "/opt/prism"

    @staticmethod
    def get_prism_path():
        path = pathlib.Path(__class__.prism_dir_path) / "prism/bin/prism"
        if not path.exists():
            raise RuntimeError(f"Prism executable not found at {path}")
        return path

    @staticmethod
    def get_prism_log_extract_script():
        path = (
            pathlib.Path(__class__.prism_dir_path)
            / "prism/etc/scripts/prism-log-extract"
        )
        if not path.exists():
            raise RuntimeError(f"Prism log script not found at {path}")
        return path

    @staticmethod
    def _call_prism(log_file: pathlib.Path, args: list[str]):
        if log_file is not None:
            args = ["-mainlog", log_file.as_posix()] + args
        subprocess_result = subprocess.run(
            [PrismCLI.get_prism_path().as_posix()] + args,
            capture_output=True,
            text=True,
        )
        reported_result = ReportedResults()
        reported_result.timeout = None
        reported_result.memout = None
        reported_result.error_code = subprocess_result.returncode
        reported_result.logfile = log_file
        if log_file is not None:
            log_subprocess_result = subprocess.run(
                [
                    PrismCLI.get_prism_log_extract_script().as_posix(),
                    "--fields=import_model_file,states,transitions",
                    reported_result.logfile,
                ],
                capture_output=True,
                text=True,
            )
            if log_subprocess_result.stderr != "":
                logger.warning(
                    "Issues parsing logfile:  " + log_subprocess_result.stderr
                )
            if log_subprocess_result.returncode != 0:
                logger.warning("Issues parsing logfile yielded error code")
            data = log_subprocess_result.stdout.split("\n")[1].split(",")
            reported_result.model_info = {"states": data[1], "transitions": data[2]}
        return reported_result

    @staticmethod
    def prism_file_to_umb(
        prism_file: pathlib.Path, output_file: pathlib.Path, log_file: pathlib.Path
    ):
        return __class__._call_prism(
            log_file, [prism_file.as_posix(), "-exportmodel", output_file.as_posix()]
        )

    @staticmethod
    def check_umb(umb_file: pathlib.Path, log_file: pathlib.Path, properties=[]):
        return __class__._call_prism(log_file, ["-importmodel", umb_file.as_posix()])

    @staticmethod
    def umb_to_umb(
        input_file: pathlib.Path, output_file: pathlib.Path, log_file: pathlib.Path
    ):
        return __class__._call_prism(
            log_file,
            [
                "-importmodel",
                input_file.as_posix(),
                "-exportmodel",
                output_file.as_posix(),
            ],
        )

    @staticmethod
    def check_process():
        result = __class__._call_prism(None, ["-version"])
        return result.error_code == 0


class StormCLI(UmbTool):
    _storm_path = "/opt/storm/build/bin/storm"

    @staticmethod
    def get_storm_path():
        path = pathlib.Path(__class__._storm_path)
        if not path.exists():
            raise RuntimeError(f"Storm executable not found at {path}")
        return path

    @staticmethod
    def _call_storm(log_file, args):
        result = subprocess.run(
            [StormCLI.get_storm_path().as_posix_path()] + args,
            capture_output=True,
            text=True,
        )
        reported_result = ReportedResults()
        reported_result.error_code = result.returncode
        reported_result.timeout = False
        reported_result.memout = False
        if log_file is not None:
            parse_logfile(result.stdout, reported_result)
            with open(log_file, "w+") as log:
                log.write(result.stdout)
        return reported_result

    @staticmethod
    def prism_file_to_umb(
        prism_file: pathlib.Path, output_file: pathlib.Path, log_file: pathlib.Path
    ):
        # Note that output_file must end with .umb for this to work.
        return __class__._call_storm(
            log_file,
            [
                "--prism",
                prism_file.as_posix(),
                "--exportbuild",
                output_file.as_posix(),
                "--buildfull",
            ],
        )

    @staticmethod
    def check_umb(umb_file: pathlib.Path, log_file=pathlib.Path, properties=[]):
        args = ["--explicit-umb", umb_file.as_posix()]
        if len(properties) > 0:
            args += ["--prop", ";".join(properties)]
        return __class__._call_storm(log_file, args)

    @staticmethod
    def umb_to_umb(
        input_file: pathlib.Path, output_file: pathlib.Path, log_file: pathlib.Path
    ):
        # Note that output_file must end with .umb for this to work.
        return __class__._call_storm(
            log_file,
            [
                "--explicit-umb",
                input_file.as_posix(),
                "--exportbuild",
                output_file.as_posix(),
            ],
        )

    @staticmethod
    def check_process():
        result = __class__._call_storm(None, ["--version"])
        return result.error_code == 0


# STORM LOGFILE Parsing
# Taken and adapted from a project by Alex Bork and Tim Quatmann
def contains_any_of(log, msg):
    for m in msg:
        if m in log:
            return True
    return False


def try_parse(log, start, before, after, out_dict, out_key, out_type):
    pos1 = log.find(before, start)
    if pos1 >= 0:
        pos1 += len(before)
        pos2 = log.find(after, pos1)
        if pos2 >= 0:
            out_dict[out_key] = out_type(log[pos1:pos2])
            return pos2 + len(after)
    return start


def parse_logfile(log, inv):
    unsupported_messages = (
        []
    )  # add messages that indicate that the invocation is not supported
    inv.not_supported = contains_any_of(log, unsupported_messages)
    memout_messages = (
        []
    )  # add messages that indicate that the invocation is not supported
    memout_messages.append(
        "An unexpected exception occurred and caused Storm to terminate. The message of this exception is: std::bad_alloc"
    )
    memout_messages.append("Return code:\t-9")
    inv.memout = contains_any_of(log, memout_messages)
    known_error_messages = (
        []
    )  # add messages that indicate a "known" error, i.e., something that indicates that no warning should be printed
    inv.anticipated_error = contains_any_of(log, known_error_messages)
    if inv.not_supported or inv.anticipated_error:
        return
    if inv.error_code not in [0, 1]:
        if not inv.timeout and not inv.memout:
            print("WARN: Unexpected return code(s): {}".format(inv["return-codes"]))

    pos = 0

    pos = try_parse(
        log,
        pos,
        "Time for model construction: ",
        "s.",
        inv,
        "model-building-time",
        float,
    )
    # if pos == 0:
    #    assert inv["timeout"] or inv["memout"], "WARN: unable to get model construction time for {}".format(inv["id"])
    #    return
    inv.model_info = dict()
    pos = try_parse(log, pos, "States: \t", "\n", inv.model_info, "states", int)
    pos = try_parse(
        log, pos, "Transitions: \t", "\n", inv.model_info, "transitions", int
    )
    pos = try_parse(log, pos, "Choices: \t", "\n", inv.model_info, "choices", int)
    pos = try_parse(
        log, pos, "Observations: \t", "\n", inv.model_info, "observations", int
    )


class UmbPython(UmbTool):

    @staticmethod
    def check_process():
        import umbi

        return True

    @staticmethod
    def umb_to_umb(
        input_file: pathlib.Path, output_file: pathlib.Path, log_file: pathlib.Path
    ):
        import umbi

        ast = umbi.read_umb(input_file)
        umbi.write_umb(ast, output_file)
        reported_results = ReportedResults()
        reported_results.model_info = ast.info.transition_system
        return reported_results
