"""Unit tests for actur.config.readconf — no live config files required."""

from unittest.mock import MagicMock, patch
import pytest

from actur.config import readconf
from actur.config.readconf import ActuConfError


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_MAIN_CONF = {
    "feedconfig": {"path": "~/feeds.toml"},
    "database": {"url": "mongodb://localhost:27017", "dbname": "actur"},
    "logfilepath": {"path": "/var/log/actur.log"},
}
_FEED_CONF = {
    "Publications": [
        {"name": "TestPub", "group": "test", "feeds": [["tf", "http://example.com/feed"]]}
    ]
}


def _toml_side_effect(main_data, feed_data):
    """Returns a side_effect callable: first call → main_data, second → feed_data."""
    results = iter([main_data, feed_data])
    return lambda fp: next(results)


def _file_mock():
    """A MagicMock that can be used as a context manager (replaces an open() return value)."""
    m = MagicMock()
    m.__enter__ = MagicMock(return_value=MagicMock())
    m.__exit__ = MagicMock(return_value=False)
    return m


# ---------------------------------------------------------------------------
# ActuConfError
# ---------------------------------------------------------------------------


def test_actu_conf_error_stores_value():
    err = ActuConfError("something went wrong")
    assert err.value == "something went wrong"


def test_actu_conf_error_str():
    assert str(ActuConfError("oops")) == "oops"


def test_actu_conf_error_is_exception():
    assert issubclass(ActuConfError, Exception)


# ---------------------------------------------------------------------------
# get_conf_by_key
# ---------------------------------------------------------------------------


def test_get_conf_by_key_raises_when_conf_is_none():
    with patch("actur.config.readconf._conf", None):
        with pytest.raises(Exception, match="No configuration data"):
            readconf.get_conf_by_key("database")


def test_get_conf_by_key_raises_when_key_is_missing():
    with patch("actur.config.readconf._conf", {"database": {}}):
        with pytest.raises(Exception, match="missing"):
            readconf.get_conf_by_key("nonexistent_key")


def test_get_conf_by_key_returns_dict_value():
    conf = {"database": {"url": "mongodb://localhost", "dbname": "testdb"}}
    with patch("actur.config.readconf._conf", conf):
        result = readconf.get_conf_by_key("database")
    assert result == {"url": "mongodb://localhost", "dbname": "testdb"}


def test_get_conf_by_key_returns_list_value():
    conf = {"Publications": [{"name": "FT"}, {"name": "LeMonde"}]}
    with patch("actur.config.readconf._conf", conf):
        result = readconf.get_conf_by_key("Publications")
    assert result == [{"name": "FT"}, {"name": "LeMonde"}]


def test_get_conf_by_key_returns_string_value():
    conf = {"logfilepath": "/var/log/actur.log"}
    with patch("actur.config.readconf._conf", conf):
        result = readconf.get_conf_by_key("logfilepath")
    assert result == "/var/log/actur.log"


# ---------------------------------------------------------------------------
# read_conf — env var and path resolution
# ---------------------------------------------------------------------------


def test_read_conf_uses_acturconf_env_var():
    """ACTURCONF env var should be opened as the main config file."""
    original = readconf._conf
    opened_paths = []

    def open_side_effect(path, *args, **kwargs):
        opened_paths.append(path)
        return _file_mock()

    try:
        with patch("os.getenv", return_value="/custom/config.toml"), \
             patch("os.path.expanduser", side_effect=lambda p: p), \
             patch("builtins.open", side_effect=open_side_effect), \
             patch("tomllib.load", side_effect=_toml_side_effect(_MAIN_CONF, _FEED_CONF)):
            readconf.read_conf()
        assert "/custom/config.toml" in opened_paths
    finally:
        readconf._conf = original


def test_read_conf_uses_default_path_when_no_env_var(capsys):
    """When ACTURCONF is unset, read_conf should print a notice and use the default path."""
    original = readconf._conf
    try:
        with patch("os.getenv", return_value=None), \
             patch("os.path.expanduser", side_effect=lambda p: p.replace("~", "/home/user")), \
             patch("builtins.open", side_effect=lambda *a, **kw: _file_mock()), \
             patch("tomllib.load", side_effect=_toml_side_effect(_MAIN_CONF, _FEED_CONF)):
            readconf.read_conf()
        out = capsys.readouterr().out
        assert "No ACTURCONF" in out
        assert "/home/user/.actur/default.toml" in out
    finally:
        readconf._conf = original


def test_read_conf_merges_feed_conf_into_main():
    """After read_conf, _conf should contain keys from both main and feed configs."""
    original = readconf._conf
    try:
        with patch("os.getenv", return_value="/config.toml"), \
             patch("os.path.expanduser", side_effect=lambda p: p), \
             patch("builtins.open", side_effect=lambda *a, **kw: _file_mock()), \
             patch("tomllib.load", side_effect=_toml_side_effect(_MAIN_CONF, _FEED_CONF)):
            readconf.read_conf()
        assert readconf._conf["database"]["dbname"] == "actur"
        assert readconf._conf["Publications"][0]["name"] == "TestPub"
    finally:
        readconf._conf = original


def test_read_conf_expands_user_in_conf_path():
    """os.path.expanduser should be applied to the main conf path."""
    original = readconf._conf
    expanded = []

    def capture_expand(p):
        expanded.append(p)
        return p.replace("~", "/home/testuser")

    try:
        with patch("os.getenv", return_value="~/myconf.toml"), \
             patch("os.path.expanduser", side_effect=capture_expand), \
             patch("builtins.open", side_effect=lambda *a, **kw: _file_mock()), \
             patch("tomllib.load", side_effect=_toml_side_effect(_MAIN_CONF, _FEED_CONF)):
            readconf.read_conf()
        assert "~/myconf.toml" in expanded
    finally:
        readconf._conf = original


def test_read_conf_expands_user_in_feed_conf_path():
    """os.path.expanduser should be applied to the feed config path from the main conf."""
    original = readconf._conf
    expanded = []

    def capture_expand(p):
        expanded.append(p)
        return p.replace("~", "/home/testuser")

    try:
        with patch("os.getenv", return_value="/config.toml"), \
             patch("os.path.expanduser", side_effect=capture_expand), \
             patch("builtins.open", side_effect=lambda *a, **kw: _file_mock()), \
             patch("tomllib.load", side_effect=_toml_side_effect(_MAIN_CONF, _FEED_CONF)):
            readconf.read_conf()
        assert _MAIN_CONF["feedconfig"]["path"] in expanded
    finally:
        readconf._conf = original


# ---------------------------------------------------------------------------
# read_conf — error handling
# ---------------------------------------------------------------------------


def test_read_conf_raises_actu_conf_error_when_main_conf_missing():
    original = readconf._conf
    try:
        with patch("os.getenv", return_value="/nonexistent/config.toml"), \
             patch("os.path.expanduser", side_effect=lambda p: p), \
             patch("builtins.open", side_effect=FileNotFoundError("no such file")):
            with pytest.raises(ActuConfError, match="Error reading configuration"):
                readconf.read_conf()
    finally:
        readconf._conf = original


def test_read_conf_raises_actu_conf_error_when_feed_conf_missing():
    original = readconf._conf
    call_count = [0]

    def open_side_effect(path, *args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 2:
            raise FileNotFoundError("feeds.toml not found")
        return _file_mock()

    try:
        with patch("os.getenv", return_value="/config.toml"), \
             patch("os.path.expanduser", side_effect=lambda p: p), \
             patch("builtins.open", side_effect=open_side_effect), \
             patch("tomllib.load", return_value=_MAIN_CONF):
            with pytest.raises(ActuConfError, match="Error reading configuration"):
                readconf.read_conf()
    finally:
        readconf._conf = original


def test_read_conf_raises_actu_conf_error_on_malformed_toml():
    original = readconf._conf
    try:
        with patch("os.getenv", return_value="/config.toml"), \
             patch("os.path.expanduser", side_effect=lambda p: p), \
             patch("builtins.open", side_effect=lambda *a, **kw: _file_mock()), \
             patch("tomllib.load", side_effect=ValueError("invalid toml")):
            with pytest.raises(ActuConfError, match="Error reading configuration"):
                readconf.read_conf()
    finally:
        readconf._conf = original


def test_read_conf_raises_actu_conf_error_when_feedconfig_key_missing():
    """Main conf without 'feedconfig' key should raise ActuConfError."""
    bad_conf = {"database": {"url": "x", "dbname": "y"}}  # no feedconfig key
    original = readconf._conf
    try:
        with patch("os.getenv", return_value="/config.toml"), \
             patch("os.path.expanduser", side_effect=lambda p: p), \
             patch("builtins.open", side_effect=lambda *a, **kw: _file_mock()), \
             patch("tomllib.load", return_value=bad_conf):
            with pytest.raises(ActuConfError, match="Error reading configuration"):
                readconf.read_conf()
    finally:
        readconf._conf = original
