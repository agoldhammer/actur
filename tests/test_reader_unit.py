"""Unit tests for actur.reader — no live config, DB, or network calls required."""

import asyncio
import datetime
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import feedparser
import pytest

from actur import reader
from actur.utils.feeds import Feed, Publication


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


class MockEntry(dict):
    """Dict subclass with attribute-style access, mimicking feedparser entries."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


def _make_entry(
    title="Test Title",
    summary="Test summary text",
    published_parsed=(2024, 1, 15, 12, 0, 0, 0, 15, 0),
):
    return MockEntry(
        title=title,
        summary=summary,
        published_parsed=published_parsed,
        summary_detail="detail",
        title_detail="detail",
        guidislink=False,
        media_credit="credit",
    )


def _make_feed_result(entries=None, bozo=False):
    result = MagicMock()
    result.bozo = bozo
    result.bozo_exception = Exception("bad xml")
    result.entries = entries if entries is not None else []
    return result


def _make_feed(name="test-feed", url="https://example.com/rss"):
    return Feed(name=name, url=url)


def _make_pub(name="TestPub", group="testgroup", pub_feeds=None):
    if pub_feeds is None:
        pub_feeds = [_make_feed()]
    return Publication(name=name, group=group, feeds=pub_feeds)


def _mock_logger():
    return MagicMock(spec=logging.Logger)


def _run(coro):
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# pcounters
# ---------------------------------------------------------------------------


def test_pcounters_returns_four_callables():
    result = reader.pcounters()
    assert len(result) == 4
    assert all(callable(fn) for fn in result)


def test_pcounters_bump_processed_increments_local_count():
    bump_processed, _, _, counts2str = reader.pcounters()
    bump_processed()
    bump_processed()
    assert "Processed: 2" in counts2str()


def test_pcounters_bump_added_increments_local_count():
    _, bump_added, _, counts2str = reader.pcounters()
    bump_added()
    assert "Added: 1" in counts2str()


def test_pcounters_bump_skipped_increments_local_count():
    _, _, bump_skipped, counts2str = reader.pcounters()
    bump_skipped()
    bump_skipped()
    bump_skipped()
    assert "Skipped: 3" in counts2str()


def test_pcounters_counts2str_includes_all_three_counters():
    bump_processed, bump_added, bump_skipped, counts2str = reader.pcounters()
    bump_processed()
    bump_added()
    bump_skipped()
    s = counts2str()
    assert "Processed: 1" in s
    assert "Added: 1" in s
    assert "Skipped: 1" in s


def test_pcounters_bump_processed_increments_global():
    original = reader._total_processed
    try:
        reader._total_processed = 0
        bump_processed, _, _, _ = reader.pcounters()
        bump_processed()
        bump_processed()
        assert reader._total_processed == 2
    finally:
        reader._total_processed = original


def test_pcounters_bump_added_increments_global():
    original = reader._total_added
    try:
        reader._total_added = 0
        _, bump_added, _, _ = reader.pcounters()
        bump_added()
        assert reader._total_added == 1
    finally:
        reader._total_added = original


def test_pcounters_bump_skipped_increments_global():
    original = reader._total_skipped
    try:
        reader._total_skipped = 0
        _, _, bump_skipped, _ = reader.pcounters()
        bump_skipped()
        assert reader._total_skipped == 1
    finally:
        reader._total_skipped = original


def test_pcounters_independent_counter_sets():
    bump_a, _, _, counts_a = reader.pcounters()
    bump_b, _, _, counts_b = reader.pcounters()
    bump_a()
    bump_a()
    assert "Processed: 2" in counts_a()
    assert "Processed: 0" in counts_b()


# ---------------------------------------------------------------------------
# process_feed
# ---------------------------------------------------------------------------


def test_process_feed_returns_empty_list_when_silent_and_no_entries():
    feed_result = _make_feed_result()
    lines = _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert lines == []


def test_process_feed_not_silent_includes_feed_name():
    feed = _make_feed(name="my-feed")
    feed_result = _make_feed_result()
    lines = _run(reader.process_feed(feed_result, feed, "TestPub", silent=False, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert any("my-feed" in line for line in lines)


def test_process_feed_not_silent_includes_entry_count():
    entry = _make_entry()
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=True):
        lines = _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=False, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert any("no. entries 1" in line for line in lines)


def test_process_feed_bozo_appends_warning_when_not_silent():
    # us-ascii bozo exceptions are appended to the printed lines instead of logged
    feed = _make_feed(name="bad-feed")
    feed_result = _make_feed_result(bozo=True)
    feed_result.bozo_exception = Exception("document declared as us-ascii, but parsed as utf-8")
    with patch("actur.utils.sentry_helper.sentry_output", new_callable=AsyncMock):
        lines = _run(reader.process_feed(feed_result, feed, "TestPub", silent=False, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert any("bozo error" in line for line in lines)


def test_process_feed_bozo_logs_error_when_no_logging_false():
    feed_result = _make_feed_result(bozo=True)
    mock_log = _mock_logger()
    with patch("actur.utils.sentry_helper.sentry_output", new_callable=AsyncMock):
        # silent=False required: bozo logging is only reached inside the `if not silent` block
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=False, no_logging=False, categorize=False, no_store=False, logger=mock_log))
    mock_log.error.assert_called_once()


def test_process_feed_bozo_skips_log_when_no_logging_true():
    feed_result = _make_feed_result(bozo=True)
    mock_log = _mock_logger()
    with patch("actur.utils.sentry_helper.sentry_output", new_callable=AsyncMock):
        # silent=False to reach the bozo block; no_logging=True to skip the logger call
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=False, no_logging=True, categorize=False, no_store=False, logger=mock_log))
    mock_log.error.assert_not_called()


def test_process_feed_skips_entry_already_in_db():
    entry = _make_entry()
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=True), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock) as mock_save:
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    mock_save.assert_not_called()


def test_process_feed_saves_new_entry():
    entry = _make_entry()
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=False), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock) as mock_save:
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    mock_save.assert_called_once_with(entry)


def test_process_feed_strips_noisy_fields_from_new_entry():
    entry = _make_entry()
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=False), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock):
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    for field in ("summary_detail", "title_detail", "guidislink", "media_credit"):
        assert field not in entry, f"Expected {field!r} to be stripped from entry"


def test_process_feed_sets_pubname_and_feedname_on_new_entry():
    entry = _make_entry()
    feed = _make_feed(name="rss-feed")
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=False), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock):
        _run(reader.process_feed(feed_result, feed, "MyPub", silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert entry["pubname"] == "MyPub"
    assert entry["feedname"] == "rss-feed"


def test_process_feed_sets_pubdate_from_published_parsed():
    entry = _make_entry(published_parsed=(2024, 3, 15, 10, 30, 0, 0, 75, 0))
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=True):
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert entry["pubdate"] == datetime.datetime(2024, 3, 15, 10, 30, 0)


def test_process_feed_skips_pubdate_when_published_parsed_is_none():
    entry = _make_entry(published_parsed=None)
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=True):
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert "pubdate" not in entry


def test_process_feed_sets_cat_to_uncategorized_without_categorize():
    entry = _make_entry()
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=False), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock):
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert entry["cat"] == "uncategorized"


def test_process_feed_calls_classify_and_sets_cat_when_categorize():
    entry = _make_entry(title="Fed raises rates")
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=False), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock), \
         patch("actur.reader.classify_by_title", new_callable=AsyncMock, return_value="Finance") as mock_clf:
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=True, no_store=False, logger=_mock_logger()))
    mock_clf.assert_called_once_with("Fed raises rates")
    assert entry["cat"] == "Finance"


def test_process_feed_classifier_exception_defaults_cat_to_uncategorized():
    entry = _make_entry()
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=False), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock), \
         patch("actur.reader.classify_by_title", new_callable=AsyncMock, side_effect=RuntimeError("timeout")), \
         patch("actur.utils.sentry_helper.sentry_output", new_callable=AsyncMock):
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=True, no_store=False, logger=_mock_logger()))
    assert entry["cat"] == "uncategorized"


def test_process_feed_classifier_exception_logs_error():
    entry = _make_entry()
    feed_result = _make_feed_result(entries=[entry])
    mock_log = _mock_logger()
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=False), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock), \
         patch("actur.reader.classify_by_title", new_callable=AsyncMock, side_effect=RuntimeError("timeout")), \
         patch("actur.utils.sentry_helper.sentry_output", new_callable=AsyncMock):
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=False, categorize=True, no_store=False, logger=mock_log))
    mock_log.error.assert_called_once()


def test_process_feed_classifier_exception_no_logging_skips_log():
    entry = _make_entry()
    feed_result = _make_feed_result(entries=[entry])
    mock_log = _mock_logger()
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=False), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock), \
         patch("actur.reader.classify_by_title", new_callable=AsyncMock, side_effect=RuntimeError("timeout")), \
         patch("actur.utils.sentry_helper.sentry_output", new_callable=AsyncMock):
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=True, no_store=False, logger=mock_log))
    mock_log.error.assert_not_called()


def test_process_feed_no_store_skips_save_article():
    entry = _make_entry()
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=False), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock) as mock_save:
        _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=False, no_store=True, logger=_mock_logger()))
    mock_save.assert_not_called()


def test_process_feed_no_store_appends_would_have_stored_line():
    entry = _make_entry(title="Big news")
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=False), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock):
        lines = _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=False, no_store=True, logger=_mock_logger()))
    combined = "\n".join(lines)
    assert "Would have stored" in combined
    assert "Big news" in combined


def test_process_feed_not_silent_appends_saving_line_for_new_entry():
    entry = _make_entry(title="Breaking news")
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=False), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock):
        lines = _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=False, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    combined = "\n".join(lines)
    assert "saving" in combined
    assert "Breaking news" in combined


def test_process_feed_not_silent_appends_counts_summary():
    entry = _make_entry()
    feed_result = _make_feed_result(entries=[entry])
    with patch("actur.utils.dbif.is_summary_in_db", new_callable=AsyncMock, return_value=False), \
         patch("actur.utils.dbif.save_article", new_callable=AsyncMock):
        lines = _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=False, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    combined = "\n".join(lines)
    assert "Processed:" in combined
    assert "Added:" in combined
    assert "Skipped:" in combined


def test_process_feed_returns_list():
    feed_result = _make_feed_result()
    result = _run(reader.process_feed(feed_result, _make_feed(), "TestPub", silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# fetch_feed
# ---------------------------------------------------------------------------


def test_fetch_feed_returns_parsed_result():
    feed_result = _make_feed_result()
    with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=feed_result):
        result = _run(reader.fetch_feed(_make_feed(), silent=True, no_logging=True, logger=_mock_logger()))
    assert result is feed_result


def test_fetch_feed_returns_none_on_timeout():
    async def _hang(*args, **kwargs):
        await asyncio.sleep(10)

    with patch("asyncio.to_thread", side_effect=_hang), \
         patch("actur.reader.FEED_FETCH_TIMEOUT", 0.01):
        result = _run(reader.fetch_feed(_make_feed(), silent=True, no_logging=True, logger=_mock_logger()))
    assert result is None


def test_fetch_feed_logs_error_on_timeout():
    async def _hang(*args, **kwargs):
        await asyncio.sleep(10)

    mock_log = _mock_logger()
    with patch("asyncio.to_thread", side_effect=_hang), \
         patch("actur.reader.FEED_FETCH_TIMEOUT", 0.01):
        _run(reader.fetch_feed(_make_feed(), silent=True, no_logging=False, logger=mock_log))
    mock_log.error.assert_called_once()


def test_fetch_feed_no_logging_skips_log_on_timeout():
    async def _hang(*args, **kwargs):
        await asyncio.sleep(10)

    mock_log = _mock_logger()
    with patch("asyncio.to_thread", side_effect=_hang), \
         patch("actur.reader.FEED_FETCH_TIMEOUT", 0.01):
        _run(reader.fetch_feed(_make_feed(), silent=True, no_logging=True, logger=mock_log))
    mock_log.error.assert_not_called()


# ---------------------------------------------------------------------------
# parse_pub
# ---------------------------------------------------------------------------


def test_parse_pub_skips_process_feed_for_timed_out_fetch():
    feed1 = _make_feed("f1", "https://a.com")
    feed2 = _make_feed("f2", "https://b.com")
    pub = _make_pub(pub_feeds=[feed1, feed2])
    with patch("actur.reader.fetch_feed", new_callable=AsyncMock, side_effect=[_make_feed_result(), None]), \
         patch("actur.reader.process_feed", new_callable=AsyncMock, return_value=[]) as mock_pf:
        _run(reader.parse_pub(pub, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert mock_pf.call_count == 1


def test_parse_pub_fetches_feedparser_result_via_to_thread():
    feed1 = _make_feed("f1", "https://a.com")
    feed2 = _make_feed("f2", "https://b.com")
    pub = _make_pub(pub_feeds=[feed1, feed2])
    feed_result = _make_feed_result()
    with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=feed_result) as mock_tt, \
         patch("actur.reader.process_feed", new_callable=AsyncMock, return_value=[]):
        _run(reader.parse_pub(pub, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert mock_tt.call_count == 2
    urls = {call.args[1] for call in mock_tt.call_args_list}
    assert mock_tt.call_args_list[0].args[0] is feedparser.parse
    assert urls == {"https://a.com", "https://b.com"}


def test_parse_pub_calls_process_feed_for_each_feed():
    feed1 = _make_feed("f1", "https://a.com")
    feed2 = _make_feed("f2", "https://b.com")
    pub = _make_pub(pub_feeds=[feed1, feed2])
    with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=_make_feed_result()), \
         patch("actur.reader.process_feed", new_callable=AsyncMock, return_value=[]) as mock_pf:
        _run(reader.parse_pub(pub, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert mock_pf.call_count == 2


def test_parse_pub_prints_pub_name_when_not_silent(capsys):
    pub = _make_pub(name="Reuters")
    with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=_make_feed_result()), \
         patch("actur.reader.process_feed", new_callable=AsyncMock, return_value=[]):
        _run(reader.parse_pub(pub, silent=False, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert "Reuters" in capsys.readouterr().out


def test_parse_pub_silent_suppresses_pub_name(capsys):
    pub = _make_pub(name="Reuters")
    with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=_make_feed_result()), \
         patch("actur.reader.process_feed", new_callable=AsyncMock, return_value=[]):
        _run(reader.parse_pub(pub, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert "Reuters" not in capsys.readouterr().out


def test_parse_pub_prints_lines_returned_by_process_feed(capsys):
    pub = _make_pub()
    with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=_make_feed_result()), \
         patch("actur.reader.process_feed", new_callable=AsyncMock, return_value=["line one", "line two"]):
        _run(reader.parse_pub(pub, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    out = capsys.readouterr().out
    assert "line one" in out
    assert "line two" in out


def test_parse_pub_prints_done_message_when_not_silent(capsys):
    pub = _make_pub(name="FT")
    with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=_make_feed_result()), \
         patch("actur.reader.process_feed", new_callable=AsyncMock, return_value=[]):
        _run(reader.parse_pub(pub, silent=False, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert "Done with pub FT" in capsys.readouterr().out


def test_parse_pub_silent_suppresses_done_message(capsys):
    pub = _make_pub(name="FT")
    with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=_make_feed_result()), \
         patch("actur.reader.process_feed", new_callable=AsyncMock, return_value=[]):
        _run(reader.parse_pub(pub, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert "Done with pub FT" not in capsys.readouterr().out


def test_parse_pub_passes_args_through_to_process_feed():
    pub = _make_pub(pub_feeds=[_make_feed("f1")])
    mock_log = _mock_logger()
    with patch("asyncio.to_thread", new_callable=AsyncMock, return_value=_make_feed_result()), \
         patch("actur.reader.process_feed", new_callable=AsyncMock, return_value=[]) as mock_pf:
        _run(reader.parse_pub(pub, silent=True, no_logging=True, categorize=True, no_store=True, logger=mock_log))
    # positional: d, feed, pubname, silent, no_logging, categorize, no_store, logger
    call_args = mock_pf.call_args[0]
    assert call_args[3] is True    # silent
    assert call_args[4] is True    # no_logging
    assert call_args[5] is True    # categorize
    assert call_args[6] is True    # no_store
    assert call_args[7] is mock_log


# ---------------------------------------------------------------------------
# process_pubs
# ---------------------------------------------------------------------------


def test_process_pubs_resets_global_counters():
    reader._total_processed = 99
    reader._total_added = 88
    reader._total_skipped = 77
    with patch("actur.utils.feeds.get_publications", return_value=[]), \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0):
        _run(reader.process_pubs(None, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert reader._total_processed == 0
    assert reader._total_added == 0
    assert reader._total_skipped == 0


def test_process_pubs_calls_get_publications():
    with patch("actur.utils.feeds.get_publications", return_value=[]) as mock_get, \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0):
        _run(reader.process_pubs(None, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    mock_get.assert_called_once()


def test_process_pubs_calls_parse_pub_for_each_publication():
    pubs = [_make_pub("Reuters", "english"), _make_pub("LeMonde", "french")]
    with patch("actur.utils.feeds.get_publications", return_value=pubs), \
         patch("actur.reader.parse_pub", new_callable=AsyncMock) as mock_pp, \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0):
        _run(reader.process_pubs(None, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert mock_pp.call_count == 2


def test_process_pubs_filters_out_xgroup():
    pubs = [_make_pub("Reuters", "english"), _make_pub("LeMonde", "french")]
    with patch("actur.utils.feeds.get_publications", return_value=pubs), \
         patch("actur.reader.parse_pub", new_callable=AsyncMock) as mock_pp, \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0):
        _run(reader.process_pubs("french", silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert mock_pp.call_count == 1
    processed_pub = mock_pp.call_args[0][0]
    assert processed_pub.name == "Reuters"


def test_process_pubs_no_xgroup_processes_all_publications():
    pubs = [_make_pub("Reuters", "english"), _make_pub("LeMonde", "french")]
    with patch("actur.utils.feeds.get_publications", return_value=pubs), \
         patch("actur.reader.parse_pub", new_callable=AsyncMock) as mock_pp, \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0):
        _run(reader.process_pubs(None, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert mock_pp.call_count == 2


def test_process_pubs_xgroup_matching_no_pubs_calls_parse_zero_times():
    pubs = [_make_pub("Reuters", "english")]
    with patch("actur.utils.feeds.get_publications", return_value=pubs), \
         patch("actur.reader.parse_pub", new_callable=AsyncMock) as mock_pp, \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0):
        _run(reader.process_pubs("english", silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert mock_pp.call_count == 0


def test_process_pubs_calls_get_article_count():
    with patch("actur.utils.feeds.get_publications", return_value=[]), \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=42) as mock_count:
        _run(reader.process_pubs(None, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    mock_count.assert_called_once()


def test_process_pubs_prints_summary_when_not_silent(capsys):
    with patch("actur.utils.feeds.get_publications", return_value=[]), \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=5):
        _run(reader.process_pubs(None, silent=False, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    out = capsys.readouterr().out
    assert "Tot:" in out
    assert "# of docs in db: 5" in out


def test_process_pubs_silent_suppresses_summary(capsys):
    with patch("actur.utils.feeds.get_publications", return_value=[]), \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=5):
        _run(reader.process_pubs(None, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert "Tot:" not in capsys.readouterr().out


def test_process_pubs_logs_summary_when_no_logging_false():
    mock_log = _mock_logger()
    with patch("actur.utils.feeds.get_publications", return_value=[]), \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0):
        _run(reader.process_pubs(None, silent=True, no_logging=False, categorize=False, no_store=False, logger=mock_log))
    mock_log.info.assert_called_once()


def test_process_pubs_no_logging_skips_summary_log():
    mock_log = _mock_logger()
    with patch("actur.utils.feeds.get_publications", return_value=[]), \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0):
        _run(reader.process_pubs(None, silent=True, no_logging=True, categorize=False, no_store=False, logger=mock_log))
    mock_log.info.assert_not_called()


def test_process_pubs_parse_pub_exception_is_caught_and_printed(capsys):
    pubs = [_make_pub("Reuters")]
    with patch("actur.utils.feeds.get_publications", return_value=pubs), \
         patch("actur.reader.parse_pub", new_callable=AsyncMock, side_effect=RuntimeError("network error")), \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0), \
         patch("actur.utils.sentry_helper.sentry_output", new_callable=AsyncMock):
        _run(reader.process_pubs(None, silent=False, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    out = capsys.readouterr().out
    assert "Could not read Reuters" in out
    assert "network error" in out


def test_process_pubs_parse_pub_exception_calls_sentry():
    pubs = [_make_pub("Reuters")]
    with patch("actur.utils.feeds.get_publications", return_value=pubs), \
         patch("actur.reader.parse_pub", new_callable=AsyncMock, side_effect=RuntimeError("timeout")), \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0), \
         patch("actur.utils.sentry_helper.sentry_output", new_callable=AsyncMock) as mock_sentry:
        _run(reader.process_pubs(None, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    mock_sentry.assert_called_once()


def test_process_pubs_parse_pub_exception_logs_error():
    pubs = [_make_pub("Reuters")]
    mock_log = _mock_logger()
    with patch("actur.utils.feeds.get_publications", return_value=pubs), \
         patch("actur.reader.parse_pub", new_callable=AsyncMock, side_effect=RuntimeError("timeout")), \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0), \
         patch("actur.utils.sentry_helper.sentry_output", new_callable=AsyncMock):
        _run(reader.process_pubs(None, silent=True, no_logging=False, categorize=False, no_store=False, logger=mock_log))
    mock_log.error.assert_called_once()


def test_process_pubs_parse_pub_exception_no_logging_skips_log():
    pubs = [_make_pub("Reuters")]
    mock_log = _mock_logger()
    with patch("actur.utils.feeds.get_publications", return_value=pubs), \
         patch("actur.reader.parse_pub", new_callable=AsyncMock, side_effect=RuntimeError("timeout")), \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0), \
         patch("actur.utils.sentry_helper.sentry_output", new_callable=AsyncMock):
        _run(reader.process_pubs(None, silent=True, no_logging=True, categorize=False, no_store=False, logger=mock_log))
    mock_log.error.assert_not_called()


def test_process_pubs_exception_silent_suppresses_print(capsys):
    pubs = [_make_pub("Reuters")]
    with patch("actur.utils.feeds.get_publications", return_value=pubs), \
         patch("actur.reader.parse_pub", new_callable=AsyncMock, side_effect=RuntimeError("timeout")), \
         patch("actur.utils.dbif.get_article_count", new_callable=AsyncMock, return_value=0), \
         patch("actur.utils.sentry_helper.sentry_output", new_callable=AsyncMock):
        _run(reader.process_pubs(None, silent=True, no_logging=True, categorize=False, no_store=False, logger=_mock_logger()))
    assert "Could not read" not in capsys.readouterr().out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_is_a_noop():
    assert reader.main() is None
