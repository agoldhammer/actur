import tomllib
from typing import Any

conf_file_name = "actur.toml"

_conf: None | dict[str, Any] = None


def read_conf() -> None:
    global _conf
    with open(conf_file_name, "rb") as fp:
        _conf = tomllib.load(fp)


# returns list of dicts of form
# {name: "pubname", feeds: list of {name: feedname, url: url}}
def get_pubs() -> list[dict[str, str]]:
    if _conf is None:
        raise Exception("No configuration info")
    return _conf["Publications"]
