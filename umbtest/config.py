import os
import tomllib
from pathlib import Path
from typing import TypedDict, cast

REPO_ROOT = Path(__file__).resolve().parent.parent

_TOML_CANDIDATES = (
    REPO_ROOT / "tools.toml",
    REPO_ROOT / ".docker" / "tools.toml",
)

_ENV_TOOL_KEYS: dict[str, str] = {
    "storm": "UMB_STORM",
    "prism": "UMB_PRISM",
    "modest": "UMB_MODEST",
}


class Byproducts(TypedDict, total=False):
    tmpfolder: str
    cleanup: bool


class Config(TypedDict):
    tools: dict[str, str]
    byproducts: Byproducts


def _as_str_dict(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    result: dict[str, object] = {}
    for key, item in cast(dict[object, object], value).items():
        if isinstance(key, str):
            result[key] = item
    return result


def _load_raw_config() -> dict[str, object]:
    raw: dict[str, object] = {}
    for candidate in _TOML_CANDIDATES:
        if candidate.is_file():
            with open(candidate, "rb") as config_file:
                loaded = cast(dict[str, object], tomllib.load(config_file))
            raw = loaded
            break
    return raw


def load_config() -> Config:
    """Locate tool paths, preferring env vars over tools.toml over built-in defaults."""
    raw = _load_raw_config()

    tools: dict[str, str] = {}
    raw_tools = _as_str_dict(raw.get("tools"))
    if raw_tools is not None:
        for key, value in raw_tools.items():
            if isinstance(value, str):
                tools[key] = value
    for key, env_var in _ENV_TOOL_KEYS.items():
        value = os.environ.get(env_var)
        if value:
            tools[key] = value

    byproducts: Byproducts = {}
    raw_byproducts = _as_str_dict(raw.get("byproducts"))
    if raw_byproducts is not None:
        tmpfolder = raw_byproducts.get("tmpfolder")
        if isinstance(tmpfolder, str):
            byproducts["tmpfolder"] = tmpfolder
        for key, value in raw_byproducts.items():
            if key == "cleanup":
                byproducts["cleanup"] = bool(value)
    if "UMB_TMPFOLDER" in os.environ:
        byproducts["tmpfolder"] = os.environ["UMB_TMPFOLDER"]
    if "cleanup" not in byproducts:
        byproducts["cleanup"] = True

    return {"tools": tools, "byproducts": byproducts}