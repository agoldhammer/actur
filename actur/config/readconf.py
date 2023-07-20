import os
import tomllib
from typing import Any

_conf_file_name = "~/Prog/actur/actur/actur.toml"

_conf: None | dict[str, Any] = None


def _read_conf() -> None:
    global _conf, _conf_file_name

    conf_from_env = os.getenv("ACTURCONF")
    if conf_from_env is not None:
        conf_path = os.path.expanduser(conf_from_env)
        conf_file_name = conf_path + "/" + "actur.toml"
    else:  # use default if no spec in env
        conf_file_name = os.path.expanduser(_conf_file_name)
    with open(conf_file_name, "rb") as fp:
        _conf = tomllib.load(fp)


# returns list of dicts of form
# {name: "pubname", feeds: list of {name: feedname, url: url}}
def get_conf_by_key(key: str) -> Any:
    if _conf is None or key not in _conf:
        raise Exception(f"No configuration data or key '{key}' is missing")
    return _conf[key]


_read_conf()  # call on load to initialize
