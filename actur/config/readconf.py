import os
import tomllib
from typing import Any

_default_conf_file_path = "~/Prog/actur/actur/local.toml"

_conf: None | dict[str, Any] = None


def _read_conf() -> None:
    global _conf, _conf_file_path

    # ACTURCONF, if used, shd specify full path to main conf file

    conf_from_env = os.getenv("ACTURCONF")
    if conf_from_env is not None:
        conf_file_path = os.path.expanduser(conf_from_env)
    else:  # use default if no spec in env
        conf_file_path = os.path.expanduser(_default_conf_file_path)
    with open(conf_file_path, "rb") as fp:
        _conf = tomllib.load(fp)
    feed_conf_path = os.path.expanduser(_conf["feedconfig"]["path"])
    with open(feed_conf_path, "rb") as fp:
        feed_conf = tomllib.load(fp)
        _conf |= feed_conf


# returns list of dicts of form
# {name: "pubname", feeds: list of {name: feedname, url: url}}
def get_conf_by_key(key: str) -> Any:
    if _conf is None or key not in _conf:
        raise Exception(f"No configuration data or key '{key}' is missing")
    return _conf[key]


_read_conf()  # call on load to initialize
