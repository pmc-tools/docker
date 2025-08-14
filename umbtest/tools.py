import subprocess
import pathlib
import umbi

import logging
logger = logging.getLogger(__name__)

class UmbTool:
    pass

class ReportedResults:
    def __init__(self):
        self.timeout = None
        self.memout = None
        self.error_code = None
        self.model_info = None
        self.logfile = None

    def __str__(self):
        return f"ReportedResults[{self.logfile},{self.error_code},{self.model_info},{self.timeout},{self.memout}]"


class PrismCLI(UmbTool):
    prism_dir_path = "/opt/prism/prism/bin/prism"

    @staticmethod
    def get_prism_path():
        return pathlib.Path(__class__.prism_dir_path) /  "prism/bin/prism"

    @staticmethod
    def get_prism_log_extract_script():
        return pathlib.Path(__class__.prism_dir_path) / "prism/etc/scripts/prism-log-extract"

    @staticmethod
    def _call_prism(log_file : pathlib.Path, args : list[str]):
        subprocess_result = subprocess.run([PrismCLI.get_prism_path().as_posix(), "-mainlog", log_file.as_posix()] + args, capture_output=True, text=True)
        reported_result =  ReportedResults()
        reported_result.timeout = None
        reported_result.memout = None
        reported_result.error_code = subprocess_result.returncode
        reported_result.logfile = log_file
        log_subprocess_result = subprocess.run([PrismCLI.get_prism_log_extract_script().as_posix(), "--fields=import_model_file,states,transitions", reported_result.logfile], capture_output=True, text=True)
        if log_subprocess_result.stderr != "":
            logger.warning("Issues parsing logfile:  " + log_subprocess_result.stderr)
        if log_subprocess_result.returncode != 0:
            logger.warning("Issues parsing logfile yielded error code")
        data = log_subprocess_result.stdout.split("\n")[1].split(",")
        reported_result.model_info = {"states": data[1], "transitions": data[2]}
        return reported_result

    @staticmethod
    def prism_file_to_umb(prism_file : pathlib.Path, output_file : pathlib.Path, log_file : pathlib.Path):
        return __class__._call_prism(log_file, [prism_file.as_posix(),
                     "-exportmodel", output_file.as_posix()])

    @staticmethod
    def check_umb(umb_file : pathlib.Path, log_file : pathlib.Path, properties=[]):
        return __class__._call_prism(log_file, ["-importmodel", umb_file.as_posix()])

    @staticmethod
    def umb_to_umb(input_file : pathlib.Path, output_file : pathlib.Path, log_file : pathlib.Path):
        return __class__._call_prism(log_file, ["-importmodel", input_file.as_posix(),
                        "-exportmodel", output_file.as_posix()])


class StormCLI(UmbTool):
    _storm_path = "/opt/storm/build/bin/storm"

    @staticmethod
    def _call_storm(args, log_file):
        result = subprocess.run([StormCLI._storm_path] + args, capture_output=True, text=True)
        reported_results = dict()
        reported_results["return-codes"] = result.returncode
        reported_results["timeout"] = False
        reported_results["memout"] = False
        parse_logfile(result.stdout, reported_results)
        with open(log_file, 'w+') as log:
            log.write(result.stdout)
        return reported_results

    @staticmethod
    def prism_file_to_umb(prism_file: pathlib.Path, output_file: pathlib.Path, log_file: pathlib.Path):
        # Note that output_file must end with .umb for this to work.
        return __class__._call_storm(["--prism", prism_file.as_posix(),
                                      "--exportbuild", output_file.as_posix(),
                                      "--buildfull"], log_file)

    @staticmethod
    def check_umb(umb_file: pathlib.Path, log_file=pathlib.Path, properties=[]):
        args = ["--explicit-umb", umb_file.as_posix()]
        if len(properties) > 0:
            args += ["--prop", ";".join(properties)]
        return __class__._call_storm(args, log_file)

    @staticmethod
    def umb_to_umb(input_file: pathlib.Path, output_file: pathlib.Path, log_file: pathlib.Path):
        # Note that output_file must end with .umb for this to work.
        return __class__._call_storm(["--explicit-umb", input_file.as_posix(),
                                      "--exportbuild", output_file.as_posix()], log_file)

# STORM LOGFILE Parsing
# Taken and adapted from a project by Alex Bork and Tim Quatmann
def contains_any_of(log, msg):
    for m in msg:
        if m in log: return True
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
    unsupported_messages = []  # add messages that indicate that the invocation is not supported
    inv["not-supported"] = contains_any_of(log, unsupported_messages)
    memout_messages = []  # add messages that indicate that the invocation is not supported
    memout_messages.append(
        "An unexpected exception occurred and caused Storm to terminate. The message of this exception is: std::bad_alloc")
    memout_messages.append("Return code:\t-9")
    inv["memout"] = contains_any_of(log, memout_messages)
    known_error_messages = []  # add messages that indicate a "known" error, i.e., something that indicates that no warning should be printed
    inv["expected-error"] = contains_any_of(log, known_error_messages)
    if inv["not-supported"] or inv["expected-error"]: return
    if inv["return-codes"] not in [0, 1]:
        if not inv["timeout"] and not inv["memout"]: print(
            "WARN: Unexpected return code(s): {}".format(inv["return-codes"]))

    pos = 0

    pos = try_parse(log, pos, "Time for model construction: ", "s.", inv, "model-building-time", float)
    # if pos == 0:
    #    assert inv["timeout"] or inv["memout"], "WARN: unable to get model construction time for {}".format(inv["id"])
    #    return
    inv["input-model"] = dict()
    pos = try_parse(log, pos, "States: \t", "\n", inv["input-model"], "states", int)
    pos = try_parse(log, pos, "Transitions: \t", "\n", inv["input-model"], "transitions", int)
    pos = try_parse(log, pos, "Choices: \t", "\n", inv["input-model"], "choices", int)
    pos = try_parse(log, pos, "Observations: \t", "\n", inv["input-model"], "observations", int)


class UmbPython(UmbTool):
    @staticmethod
    def umb_to_umb(input_file  : pathlib.Path, output_file  : pathlib.Path, log_file : pathlib.Path):
         ast = umbi.read_umb(input_file)
         umbi.write_umb(ast, output_file)
         reported_results = ReportedResults()
         reported_results.model_info = ast.info.transition_system
         return reported_results