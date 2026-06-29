"""Unit tests for actur.actu_cli — no live config, DB, or OpenAI calls required."""

from unittest.mock import AsyncMock, MagicMock, patch

from click.testing import CliRunner

from actur.actu_cli import cli, main
from actur.utils.feeds import Feed, Publication


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

RUNNER = CliRunner()


def _pub(name="TestPub", group="testgroup", pub_feeds=None):
    if pub_feeds is None:
        pub_feeds = [Feed("feed1", "https://a.com")]
    return Publication(name=name, group=group, feeds=pub_feeds)


# ---------------------------------------------------------------------------
# show --list
# ---------------------------------------------------------------------------


def test_show_list_calls_get_publications():
    pubs = [_pub("Reuters", "english")]
    with patch("actur.utils.feeds.get_publications", return_value=pubs) as mock_get:
        RUNNER.invoke(cli, ["show", "--list"])
    mock_get.assert_called_once()


def test_show_list_prints_pub_name_and_group():
    pubs = [_pub("Reuters", "english")]
    with patch("actur.utils.feeds.get_publications", return_value=pubs):
        result = RUNNER.invoke(cli, ["show", "--list"])
    assert "Reuters" in result.output
    assert "english" in result.output


def test_show_list_prints_feed_names():
    pub_feeds = [Feed("r-top", "https://r.com"), Feed("r-world", "https://r.com/world")]
    pubs = [_pub("Reuters", "english", pub_feeds)]
    with patch("actur.utils.feeds.get_publications", return_value=pubs):
        result = RUNNER.invoke(cli, ["show", "--list"])
    assert "r-top" in result.output
    assert "r-world" in result.output


def test_show_list_prints_multiple_publications():
    pubs = [_pub("Reuters", "english"), _pub("LeMonde", "french")]
    with patch("actur.utils.feeds.get_publications", return_value=pubs):
        result = RUNNER.invoke(cli, ["show", "--list"])
    assert "Reuters" in result.output
    assert "LeMonde" in result.output


def test_show_list_empty_publications():
    with patch("actur.utils.feeds.get_publications", return_value=[]):
        result = RUNNER.invoke(cli, ["show", "--list"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# show (article display)
# ---------------------------------------------------------------------------


def test_show_calls_query():
    mock_articles = MagicMock()
    with patch("actur.utils.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=mock_articles) as mock_q, \
         patch("actur.utils.display.display_articles", new_callable=AsyncMock):
        RUNNER.invoke(cli, ["show", "reuters"])
    mock_q.assert_called_once()


def test_show_passes_pubnames_to_query():
    mock_articles = MagicMock()
    with patch("actur.utils.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=mock_articles) as mock_q, \
         patch("actur.utils.display.display_articles", new_callable=AsyncMock):
        RUNNER.invoke(cli, ["show", "reuters", "ft"])
    pubnames = mock_q.call_args[0][0]
    assert "reuters" in pubnames
    assert "ft" in pubnames


def test_show_passes_start_to_query():
    mock_articles = MagicMock()
    with patch("actur.utils.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=mock_articles) as mock_q, \
         patch("actur.utils.display.display_articles", new_callable=AsyncMock):
        RUNNER.invoke(cli, ["show", "--start", "2024-01-01"])
    assert mock_q.call_args[0][1] == "2024-01-01"


def test_show_passes_end_to_query():
    mock_articles = MagicMock()
    with patch("actur.utils.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=mock_articles) as mock_q, \
         patch("actur.utils.display.display_articles", new_callable=AsyncMock):
        RUNNER.invoke(cli, ["show", "--end", "2024-01-31"])
    assert mock_q.call_args[0][2] == "2024-01-31"


def test_show_passes_days_to_query():
    mock_articles = MagicMock()
    with patch("actur.utils.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=mock_articles) as mock_q, \
         patch("actur.utils.display.display_articles", new_callable=AsyncMock):
        RUNNER.invoke(cli, ["show", "--days", "3"])
    assert mock_q.call_args[0][3] == 3


def test_show_passes_hours_to_query():
    mock_articles = MagicMock()
    with patch("actur.utils.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=mock_articles) as mock_q, \
         patch("actur.utils.display.display_articles", new_callable=AsyncMock):
        RUNNER.invoke(cli, ["show", "--hours", "6"])
    assert mock_q.call_args[0][4] == 6


def test_show_passes_group_to_query():
    mock_articles = MagicMock()
    with patch("actur.utils.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=mock_articles) as mock_q, \
         patch("actur.utils.display.display_articles", new_callable=AsyncMock):
        RUNNER.invoke(cli, ["show", "--group", "english"])
    assert mock_q.call_args[0][5] == "english"


def test_show_calls_display_articles_with_query_result():
    mock_articles = MagicMock()
    with patch("actur.utils.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=mock_articles), \
         patch("actur.utils.display.display_articles", new_callable=AsyncMock) as mock_display:
        RUNNER.invoke(cli, ["show"])
    mock_display.assert_called_once()
    assert mock_display.call_args[0][0] is mock_articles


def test_show_passes_summary_false_by_default():
    mock_articles = MagicMock()
    with patch("actur.utils.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=mock_articles), \
         patch("actur.utils.display.display_articles", new_callable=AsyncMock) as mock_display:
        RUNNER.invoke(cli, ["show"])
    assert mock_display.call_args[1]["summary_flag"] is False


def test_show_passes_summary_true_with_flag():
    mock_articles = MagicMock()
    with patch("actur.utils.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, return_value=mock_articles), \
         patch("actur.utils.display.display_articles", new_callable=AsyncMock) as mock_display:
        RUNNER.invoke(cli, ["show", "--summary"])
    assert mock_display.call_args[1]["summary_flag"] is True


def test_show_prints_error_on_query_exception():
    with patch("actur.utils.query.get_arts_in_daterange_from_pubs", new_callable=AsyncMock, side_effect=RuntimeError("db down")):
        result = RUNNER.invoke(cli, ["show"])
    assert "Error showing articles" in result.output
    assert "db down" in result.output


# ---------------------------------------------------------------------------
# read command
# ---------------------------------------------------------------------------


def test_read_calls_setup_logging():
    with patch("actur.reader.setup_logging") as mock_sl, \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock):
        RUNNER.invoke(cli, ["read"])
    mock_sl.assert_called_once()


def test_read_calls_ensure_indexes():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock) as mock_ei, \
         patch("actur.reader.process_pubs", new_callable=AsyncMock):
        RUNNER.invoke(cli, ["read"])
    mock_ei.assert_called_once()


def test_read_calls_process_pubs_once_without_daemon():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        RUNNER.invoke(cli, ["read"])
    mock_pp.assert_called_once()


def test_read_passes_xgroup_to_process_pubs():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        RUNNER.invoke(cli, ["read", "--xgroup", "french"])
    assert mock_pp.call_args[0][0] == "french"


def test_read_passes_silent_true_to_process_pubs():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        RUNNER.invoke(cli, ["read", "--silent"])
    assert mock_pp.call_args[0][1] is True


def test_read_passes_silent_false_by_default():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        RUNNER.invoke(cli, ["read"])
    assert mock_pp.call_args[0][1] is False


def test_read_passes_no_logging_flag():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        RUNNER.invoke(cli, ["read", "--no-logging"])
    assert mock_pp.call_args[0][2] is True


def test_read_passes_categorize_flag():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        RUNNER.invoke(cli, ["read", "--categorize"])
    assert mock_pp.call_args[0][3] is True


def test_read_passes_no_store_flag():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock) as mock_pp:
        RUNNER.invoke(cli, ["read", "--no-store"])
    assert mock_pp.call_args[0][4] is True


def test_read_prints_exiting_when_not_silent():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock):
        result = RUNNER.invoke(cli, ["read"])
    assert "Exiting..." in result.output


def test_read_silent_suppresses_exiting_message():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock):
        result = RUNNER.invoke(cli, ["read", "--silent"])
    assert "Exiting..." not in result.output


def test_read_daemon_calls_asyncio_sleep():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock), \
         patch("asyncio.sleep", new_callable=AsyncMock, side_effect=RuntimeError("stop")) as mock_sleep:
        RUNNER.invoke(cli, ["read", "--daemon"])
    mock_sleep.assert_called_once()


def test_read_daemon_sleeps_for_default_1800_seconds():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock), \
         patch("asyncio.sleep", new_callable=AsyncMock, side_effect=RuntimeError("stop")) as mock_sleep:
        RUNNER.invoke(cli, ["read", "--daemon"])
    mock_sleep.assert_called_once_with(1800)


def test_read_daemon_respects_custom_sleeptime():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock), \
         patch("asyncio.sleep", new_callable=AsyncMock, side_effect=RuntimeError("stop")) as mock_sleep:
        RUNNER.invoke(cli, ["read", "--daemon", "--sleeptime", "300"])
    mock_sleep.assert_called_once_with(300)


def test_read_daemon_prints_sleeping_message():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock), \
         patch("asyncio.sleep", new_callable=AsyncMock, side_effect=RuntimeError("stop")):
        result = RUNNER.invoke(cli, ["read", "--daemon"])
    assert "Sleeping" in result.output


def test_read_daemon_silent_suppresses_sleeping_message():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock), \
         patch("asyncio.sleep", new_callable=AsyncMock, side_effect=RuntimeError("stop")):
        result = RUNNER.invoke(cli, ["read", "--daemon", "--silent"])
    assert "Sleeping" not in result.output


def test_read_prints_error_on_process_pubs_exception():
    with patch("actur.reader.setup_logging"), \
         patch("actur.utils.dbif.ensure_indexes", new_callable=AsyncMock), \
         patch("actur.reader.process_pubs", new_callable=AsyncMock, side_effect=RuntimeError("feed broken")):
        result = RUNNER.invoke(cli, ["read"])
    assert "Could not read feeds" in result.output
    assert "feed broken" in result.output


# ---------------------------------------------------------------------------
# fix-uncategorized command
# ---------------------------------------------------------------------------


def test_fix_uncategorized_calls_function():
    with patch("actur.fix_uncategorized.fix_uncategorized", new_callable=AsyncMock, return_value=(3, 1)) as mock_fix:
        RUNNER.invoke(cli, ["fix-uncategorized"])
    mock_fix.assert_called_once()


def test_fix_uncategorized_default_dry_run_false():
    with patch("actur.fix_uncategorized.fix_uncategorized", new_callable=AsyncMock, return_value=(0, 0)) as mock_fix:
        RUNNER.invoke(cli, ["fix-uncategorized"])
    mock_fix.assert_called_once_with(dry_run=False)


def test_fix_uncategorized_dry_run_flag_passes_true():
    with patch("actur.fix_uncategorized.fix_uncategorized", new_callable=AsyncMock, return_value=(0, 0)) as mock_fix:
        RUNNER.invoke(cli, ["fix-uncategorized", "--dry-run"])
    mock_fix.assert_called_once_with(dry_run=True)


def test_fix_uncategorized_prints_fixed_and_failed_counts():
    with patch("actur.fix_uncategorized.fix_uncategorized", new_callable=AsyncMock, return_value=(5, 2)):
        result = RUNNER.invoke(cli, ["fix-uncategorized"])
    assert "Fixed: 5" in result.output
    assert "Failed: 2" in result.output


def test_fix_uncategorized_dry_run_prefixes_output():
    with patch("actur.fix_uncategorized.fix_uncategorized", new_callable=AsyncMock, return_value=(3, 0)):
        result = RUNNER.invoke(cli, ["fix-uncategorized", "--dry-run"])
    assert "[dry-run]" in result.output


def test_fix_uncategorized_prints_error_on_exception():
    with patch("actur.fix_uncategorized.fix_uncategorized", new_callable=AsyncMock, side_effect=RuntimeError("db error")):
        result = RUNNER.invoke(cli, ["fix-uncategorized"])
    assert "Error fixing uncategorized" in result.output
    assert "db error" in result.output


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_calls_init_all():
    with patch("actur.utils.init_mgr.init_all") as mock_init, \
         patch("actur.actu_cli.cli"):
        main()
    mock_init.assert_called_once()


def test_main_calls_cli():
    with patch("actur.utils.init_mgr.init_all"), \
         patch("actur.actu_cli.cli") as mock_cli:
        main()
    mock_cli.assert_called_once()
