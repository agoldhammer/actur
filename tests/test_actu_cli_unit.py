"""Unit tests for actur.actu_cli — no live config, DB, or network calls required."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

# ---------------------------------------------------------------------------
# Import actu_cli with the patches needed to satisfy the default-argument
# evaluation of GlobalLogger.get_logger() in the `read` command definition.
# ---------------------------------------------------------------------------
_import_patches = [
    patch("actur.utils.init_mgr.init_all"),
    patch("actur.config.readconf.get_conf_by_key", return_value={"path": "/dev/null"}),
    patch("os.access", return_value=True),
    patch("logging.FileHandler"),
]
for _p in _import_patches:
    _p.start()

from actur.actu_cli import cli, setup_logging, GlobalLogger  # noqa: E402

for _p in _import_patches:
    _p.stop()


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _runner():
    return CliRunner()


def _fake_pubs():
    from actur.utils.feeds import Feed, Publication
    return [
        Publication("Reuters", "english", [Feed("reuters-top", "https://example.com/rss")]),
        Publication("LeMonde", "french", [Feed("lemonde-fr", "https://example.fr/rss")]),
    ]


# ---------------------------------------------------------------------------
# setup_logging
# ---------------------------------------------------------------------------


def test_setup_logging_raises_when_path_not_writable():
    with patch("actur.actu_cli.rc.get_conf_by_key", return_value={"path": "/nonexistent/log.txt"}), \
         patch("os.access", return_value=False):
        with pytest.raises(Exception, match="does not exist or is not writable"):
            setup_logging()


def test_setup_logging_reads_logfilepath_key():
    with patch("actur.actu_cli.rc.get_conf_by_key", return_value={"path": "/dev/null"}) as mock_conf, \
         patch("os.access", return_value=True), \
         patch("logging.FileHandler"):
        setup_logging()
    mock_conf.assert_called_once_with("logfilepath")


def test_setup_logging_creates_file_handler_at_configured_path():
    with patch("actur.actu_cli.rc.get_conf_by_key", return_value={"path": "/var/log/actur.log"}), \
         patch("os.access", return_value=True), \
         patch("logging.FileHandler") as mock_fh:
        setup_logging()
    mock_fh.assert_called_once_with("/var/log/actur.log")


def test_setup_logging_returns_logger():
    with patch("actur.actu_cli.rc.get_conf_by_key", return_value={"path": "/dev/null"}), \
         patch("os.access", return_value=True), \
         patch("logging.FileHandler"):
        result = setup_logging()
    assert isinstance(result, logging.Logger)


def test_setup_logging_returns_logger_named_actu_rdr_log():
    with patch("actur.actu_cli.rc.get_conf_by_key", return_value={"path": "/dev/null"}), \
         patch("os.access", return_value=True), \
         patch("logging.FileHandler"):
        result = setup_logging()
    assert result.name == "actu-rdr-log"


# ---------------------------------------------------------------------------
# GlobalLogger.get_logger
# ---------------------------------------------------------------------------


def test_get_logger_calls_init_all():
    original = GlobalLogger._logger
    try:
        GlobalLogger._logger = None
        with patch("actur.actu_cli.init_mgr.init_all") as mock_init, \
             patch("actur.actu_cli.setup_logging", return_value=MagicMock(spec=logging.Logger)):
            GlobalLogger.get_logger()
        mock_init.assert_called_once()
    finally:
        GlobalLogger._logger = original


def test_get_logger_calls_setup_logging_when_logger_is_none():
    original = GlobalLogger._logger
    try:
        GlobalLogger._logger = None
        with patch("actur.actu_cli.init_mgr.init_all"), \
             patch("actur.actu_cli.setup_logging", return_value=MagicMock(spec=logging.Logger)) as mock_sl:
            GlobalLogger.get_logger()
        mock_sl.assert_called_once()
    finally:
        GlobalLogger._logger = original


def test_get_logger_returns_same_logger_on_repeated_calls():
    original = GlobalLogger._logger
    try:
        GlobalLogger._logger = None
        mock_log = MagicMock(spec=logging.Logger)
        with patch("actur.actu_cli.init_mgr.init_all"), \
             patch("actur.actu_cli.setup_logging", return_value=mock_log):
            first = GlobalLogger.get_logger()
            second = GlobalLogger.get_logger()
        assert first is second
    finally:
        GlobalLogger._logger = original


def test_get_logger_skips_setup_logging_when_already_initialized():
    original = GlobalLogger._logger
    try:
        GlobalLogger._logger = MagicMock(spec=logging.Logger)
        with patch("actur.actu_cli.init_mgr.init_all"), \
             patch("actur.actu_cli.setup_logging") as mock_sl:
            GlobalLogger.get_logger()
        mock_sl.assert_not_called()
    finally:
        GlobalLogger._logger = original


# ---------------------------------------------------------------------------
# show --list
# ---------------------------------------------------------------------------


def test_show_list_prints_publication_names():
    with patch("actur.actu_cli.feeds.get_publications", return_value=_fake_pubs()):
        result = _runner().invoke(cli, ["show", "--list"])
    assert result.exit_code == 0
    assert "Reuters" in result.output
    assert "LeMonde" in result.output


def test_show_list_prints_group_names():
    with patch("actur.actu_cli.feeds.get_publications", return_value=_fake_pubs()):
        result = _runner().invoke(cli, ["show", "--list"])
    assert "english" in result.output
    assert "french" in result.output


def test_show_list_prints_feed_names():
    with patch("actur.actu_cli.feeds.get_publications", return_value=_fake_pubs()):
        result = _runner().invoke(cli, ["show", "--list"])
    assert "reuters-top" in result.output
    assert "lemonde-fr" in result.output


def test_show_list_does_not_call_query():
    with patch("actur.actu_cli.feeds.get_publications", return_value=_fake_pubs()), \
         patch("actur.actu_cli.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock) as mock_q:
        _runner().invoke(cli, ["show", "--list"])
    mock_q.assert_not_called()


# ---------------------------------------------------------------------------
# show (article display)
# ---------------------------------------------------------------------------


def test_show_calls_query_with_correct_args():
    with patch("actur.actu_cli.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=[]) as mock_q, \
         patch("actur.actu_cli.display.display_articles", new_callable=AsyncMock):
        _runner().invoke(cli, ["show", "--days", "1", "Reuters"])
    mock_q.assert_called_once()
    args = mock_q.call_args[0]
    assert "Reuters" in args[0]  # pubnames tuple
    assert args[3] == 1          # days


def test_show_passes_summary_flag_to_display():
    with patch("actur.actu_cli.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=[]), \
         patch("actur.actu_cli.display.display_articles", new_callable=AsyncMock) as mock_disp:
        _runner().invoke(cli, ["show", "--summary"])
    mock_disp.assert_called_once()
    assert mock_disp.call_args.kwargs.get("summary_flag") is True


def test_show_without_summary_flag_passes_false():
    with patch("actur.actu_cli.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=[]), \
         patch("actur.actu_cli.display.display_articles", new_callable=AsyncMock) as mock_disp:
        _runner().invoke(cli, ["show"])
    assert mock_disp.call_args.kwargs.get("summary_flag") is False


def test_show_prints_error_on_exception():
    with patch("actur.actu_cli.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, side_effect=Exception("db down")):
        result = _runner().invoke(cli, ["show"])
    assert result.exit_code == 0
    assert "Error showing articles" in result.output
    assert "db down" in result.output


# ---------------------------------------------------------------------------
# read
# ---------------------------------------------------------------------------


def test_read_calls_ensure_indexes():
    with patch("actur.actu_cli.dbif.ensure_indexes", new_callable=AsyncMock) as mock_idx, \
         patch("actur.actu_cli.reader.process_pubs", new_callable=AsyncMock):
        _runner().invoke(cli, ["read", "--no-logging"])
    mock_idx.assert_called_once()


def test_read_calls_process_pubs_once_without_daemon():
    with patch("actur.actu_cli.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.actu_cli.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        _runner().invoke(cli, ["read", "--no-logging"])
    mock_pp.assert_called_once()


def test_read_passes_silent_flag_to_process_pubs():
    # process_pubs is called positionally: (xgroup, silent, no_logging, categorize, no_store, logger)
    with patch("actur.actu_cli.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.actu_cli.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        _runner().invoke(cli, ["read", "--no-logging", "--silent"])
    args = mock_pp.call_args[0]
    assert args[1] is True  # silent


def test_read_passes_no_logging_flag_to_process_pubs():
    with patch("actur.actu_cli.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.actu_cli.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        _runner().invoke(cli, ["read", "--no-logging"])
    args = mock_pp.call_args[0]  # positional: xgroup, silent, no_logging, categorize, no_store, logger
    assert args[2] is True


def test_read_passes_categorize_flag_to_process_pubs():
    with patch("actur.actu_cli.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.actu_cli.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        _runner().invoke(cli, ["read", "--no-logging", "--categorize"])
    args = mock_pp.call_args[0]
    assert args[3] is True  # categorize


def test_read_passes_no_store_flag_to_process_pubs():
    with patch("actur.actu_cli.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.actu_cli.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        _runner().invoke(cli, ["read", "--no-logging", "--no-store"])
    args = mock_pp.call_args[0]
    assert args[4] is True  # no_store


def test_read_passes_xgroup_to_process_pubs():
    with patch("actur.actu_cli.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.actu_cli.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        _runner().invoke(cli, ["read", "--no-logging", "--xgroup", "french"])
    args = mock_pp.call_args[0]
    assert args[0] == "french"  # xgroup


def test_read_prints_error_on_exception():
    with patch("actur.actu_cli.dbif.ensure_indexes", new_callable=AsyncMock, side_effect=Exception("index failed")):
        result = _runner().invoke(cli, ["read", "--no-logging"])
    assert result.exit_code == 0
    assert "Could not read feeds" in result.output
    assert "index failed" in result.output


def test_read_prints_exiting_when_not_silent():
    with patch("actur.actu_cli.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.actu_cli.reader.process_pubs", new_callable=AsyncMock):
        result = _runner().invoke(cli, ["read", "--no-logging"])
    assert "Exiting" in result.output


def test_read_silent_suppresses_exiting_message():
    with patch("actur.actu_cli.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.actu_cli.reader.process_pubs", new_callable=AsyncMock):
        result = _runner().invoke(cli, ["read", "--no-logging", "--silent"])
    assert "Exiting" not in result.output


# ---------------------------------------------------------------------------
# fix-uncategorized
# ---------------------------------------------------------------------------


def test_fix_uncategorized_calls_fix_uncategorized():
    with patch("actur.actu_cli.fix_uncategorized.fix_uncategorized", new_callable=AsyncMock, return_value=(3, 1)) as mock_fix:
        result = _runner().invoke(cli, ["fix-uncategorized"])
    mock_fix.assert_called_once_with(dry_run=False)
    assert result.exit_code == 0


def test_fix_uncategorized_dry_run_passes_flag():
    with patch("actur.actu_cli.fix_uncategorized.fix_uncategorized", new_callable=AsyncMock, return_value=(0, 0)) as mock_fix:
        _runner().invoke(cli, ["fix-uncategorized", "--dry-run"])
    mock_fix.assert_called_once_with(dry_run=True)


def test_fix_uncategorized_prints_counts():
    with patch("actur.actu_cli.fix_uncategorized.fix_uncategorized", new_callable=AsyncMock, return_value=(5, 2)):
        result = _runner().invoke(cli, ["fix-uncategorized"])
    assert "Fixed: 5" in result.output
    assert "Failed: 2" in result.output


def test_fix_uncategorized_dry_run_prefixes_output():
    with patch("actur.actu_cli.fix_uncategorized.fix_uncategorized", new_callable=AsyncMock, return_value=(1, 0)):
        result = _runner().invoke(cli, ["fix-uncategorized", "--dry-run"])
    assert "[dry-run]" in result.output


def test_fix_uncategorized_prints_error_on_exception():
    with patch("actur.actu_cli.fix_uncategorized.fix_uncategorized", new_callable=AsyncMock, side_effect=Exception("openai down")):
        result = _runner().invoke(cli, ["fix-uncategorized"])
    assert "Error fixing uncategorized" in result.output
    assert "openai down" in result.output


# ---------------------------------------------------------------------------
# version flag
# ---------------------------------------------------------------------------


def test_version_flag_exits_zero():
    result = _runner().invoke(cli, ["--version"])
    assert result.exit_code == 0


def test_version_short_flag_exits_zero():
    result = _runner().invoke(cli, ["-v"])
    assert result.exit_code == 0


def test_version_output_contains_actu():
    result = _runner().invoke(cli, ["--version"])
    assert "actu" in result.output
