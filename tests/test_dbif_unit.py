"""Unit tests for actur.utils.dbif — no live DB or config required."""

import asyncio
from bson import ObjectId
from unittest.mock import AsyncMock, MagicMock, patch, call

import pendulum
import pymongo
import pytest

from actur.utils import dbif
from actur.utils.dbif import ActuDBError


class AsyncIterMock:
    """Wraps a plain iterable to support `async for`."""

    def __init__(self, items):
        self._items = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._items)
        except StopIteration:
            raise StopAsyncIteration


@pytest.fixture
def mock_db():
    """Patch _client/_dbname so get_db() returns a fresh MagicMock database."""
    db = MagicMock()
    client = MagicMock()
    client.__getitem__.return_value = db
    with patch("actur.utils.dbif._client", client), patch(
        "actur.utils.dbif._dbname", "testdb"
    ):
        yield db


# ---------------------------------------------------------------------------
# get_db
# ---------------------------------------------------------------------------


def test_get_db_raises_when_not_initialized():
    with patch("actur.utils.dbif._dbname", None):
        with pytest.raises(ActuDBError):
            dbif.get_db()


def test_get_db_returns_database(mock_db):
    assert dbif.get_db() is mock_db


# ---------------------------------------------------------------------------
# init_db
# ---------------------------------------------------------------------------


def test_init_db_sets_globals():
    original = (dbif._host, dbif._client, dbif._dbname)
    conf = {"url": "mongodb://localhost:27017", "dbname": "testdb"}
    try:
        with patch("actur.utils.dbif.rc.get_conf_by_key", return_value=conf), patch(
            "actur.utils.dbif.AsyncMongoClient"
        ) as mock_cls:
            dbif.init_db()
            assert dbif._host == conf["url"]
            assert dbif._dbname == conf["dbname"]
            mock_cls.assert_called_once_with(conf["url"])
    finally:
        dbif._host, dbif._client, dbif._dbname = original


def test_init_db_raises_on_config_error():
    original = (dbif._host, dbif._client, dbif._dbname)
    try:
        with patch(
            "actur.utils.dbif.rc.get_conf_by_key",
            side_effect=Exception("missing key"),
        ):
            with pytest.raises(ActuDBError, match="Error initializing database"):
                dbif.init_db()
    finally:
        dbif._host, dbif._client, dbif._dbname = original


# ---------------------------------------------------------------------------
# save_article
# ---------------------------------------------------------------------------


def test_save_article_calls_insert_one(mock_db):
    mock_db.articles.insert_one = AsyncMock()
    entry = {"title": "Test", "summary": "body"}
    asyncio.run(dbif.save_article(entry))
    mock_db.articles.insert_one.assert_called_once_with(entry)


# ---------------------------------------------------------------------------
# get_article_count
# ---------------------------------------------------------------------------


def test_get_article_count_returns_count(mock_db):
    mock_db.articles.count_documents = AsyncMock(return_value=42)
    assert asyncio.run(dbif.get_article_count()) == 42
    mock_db.articles.count_documents.assert_called_once_with({})


# ---------------------------------------------------------------------------
# is_summary_in_db
# ---------------------------------------------------------------------------


def test_is_summary_in_db_returns_true_when_matching(mock_db):
    mock_db.articles.find.return_value = AsyncIterMock(
        [{"hash": "abc123", "summary": "hello world"}]
    )
    assert asyncio.run(dbif.is_summary_in_db("abc123", "hello world")) is True


def test_is_summary_in_db_returns_false_when_no_hash_match(mock_db):
    mock_db.articles.find.return_value = AsyncIterMock([])
    assert asyncio.run(dbif.is_summary_in_db("deadbeef", "hello world")) is False


def test_is_summary_in_db_returns_false_when_summary_differs(mock_db):
    mock_db.articles.find.return_value = AsyncIterMock(
        [{"hash": "abc123", "summary": "different text"}]
    )
    assert asyncio.run(dbif.is_summary_in_db("abc123", "hello world")) is False


# ---------------------------------------------------------------------------
# find_text
# ---------------------------------------------------------------------------


def test_find_text_passes_text_query(mock_db):
    mock_coll = mock_db.__getitem__.return_value
    dbif.find_text("articles", "climate")
    mock_db.__getitem__.assert_called_with("articles")
    mock_coll.find.assert_called_once_with({"$text": {"$search": "climate"}})
    mock_coll.find.return_value.sort.assert_called_once_with("pubdate", 1)


# ---------------------------------------------------------------------------
# find_articles_by_pubname
# ---------------------------------------------------------------------------


def test_find_articles_by_pubname(mock_db):
    mock_cursor = MagicMock()
    mock_db.articles.find.return_value = mock_cursor
    result = dbif.find_articles_by_pubname("LeMonde")
    mock_db.articles.find.assert_called_once_with(
        {"pubname": "LeMonde"}, {"pubdate": 1}
    )
    assert result is mock_cursor


# ---------------------------------------------------------------------------
# find_articles_by_daterange
# ---------------------------------------------------------------------------


def test_find_articles_by_daterange(mock_db):
    mock_cursor = MagicMock()
    mock_db.articles.find.return_value = mock_cursor
    start = pendulum.datetime(2024, 1, 1)
    end = pendulum.datetime(2024, 1, 2)
    result = dbif.find_articles_by_daterange(start, end)
    mock_db.articles.find.assert_called_once_with(
        {"pubdate": {"$gte": start, "$lte": end}},
        {"pubdate": 1, "pubname": 1, "summary": 1, "title": 1, "cat": 1},
    )
    assert result is mock_cursor


# ---------------------------------------------------------------------------
# make_tempdb_from_daterange
# ---------------------------------------------------------------------------


def test_make_tempdb_aggregates_and_creates_indexes(mock_db):
    mock_cursor = AsyncMock()
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_db.articles.aggregate = AsyncMock(return_value=mock_cursor)
    mock_db.daterange.create_index = AsyncMock()

    start = pendulum.datetime(2024, 1, 1)
    end = pendulum.datetime(2024, 1, 2)
    asyncio.run(dbif.make_tempdb_from_daterange(start, end))

    mock_db.articles.aggregate.assert_called_once_with(
        [
            {"$match": {"pubdate": {"$gte": start, "$lte": end}}},
            {"$out": "daterange"},
        ]
    )
    mock_cursor.to_list.assert_called_once_with(length=None)
    assert mock_db.daterange.create_index.call_count == 2


# ---------------------------------------------------------------------------
# today_range
# ---------------------------------------------------------------------------


def test_today_range_returns_consecutive_days():
    today, tomorrow = dbif.today_range()
    assert isinstance(today, pendulum.DateTime)
    assert isinstance(tomorrow, pendulum.DateTime)
    assert tomorrow > today


# ---------------------------------------------------------------------------
# get_articles_in_daterange
# ---------------------------------------------------------------------------


def test_get_articles_in_daterange_queries_daterange_collection(mock_db):
    mock_sorted = MagicMock()
    mock_db.daterange.find.return_value.sort.return_value = mock_sorted
    pubnames = ["LeMonde", "FT"]

    result = dbif.get_articles_in_daterange(pubnames)

    mock_db.daterange.find.assert_called_once_with(
        {"pubname": {"$in": pubnames}},
        {
            "pubdate": 1,
            "pubname": 1,
            "summary": 1,
            "title": 1,
            "link": 1,
            "published": 1,
            "published_parsed": 1,
            "cat": 1,
        },
    )
    mock_db.daterange.find.return_value.sort.assert_called_once_with("pubdate", 1)
    assert result is mock_sorted


# ---------------------------------------------------------------------------
# cursor_to_json
# ---------------------------------------------------------------------------


def test_cursor_to_json_returns_valid_json():
    import json

    data = [{"title": "hello", "count": 1}]
    result = dbif.cursor_to_json(data)
    assert json.loads(result) == data


# ---------------------------------------------------------------------------
# get_uncategorized_articles
# ---------------------------------------------------------------------------


def test_get_uncategorized_articles_uses_correct_query(mock_db):
    mock_cursor = MagicMock()
    mock_db.articles.find.return_value = mock_cursor
    result = dbif.get_uncategorized_articles()
    mock_db.articles.find.assert_called_once_with(
        {"$or": [{"cat": {"$exists": False}}, {"cat": "uncategorized"}]},
        {"_id": 1, "title": 1},
    )
    assert result is mock_cursor


# ---------------------------------------------------------------------------
# update_article_cat
# ---------------------------------------------------------------------------


def test_update_article_cat_calls_update_one(mock_db):
    mock_db.articles.update_one = AsyncMock()
    article_id = ObjectId()
    asyncio.run(dbif.update_article_cat(article_id, "technology"))
    mock_db.articles.update_one.assert_called_once_with(
        {"_id": article_id}, {"$set": {"cat": "technology"}}
    )


# ---------------------------------------------------------------------------
# ensure_indexes
# ---------------------------------------------------------------------------


def test_ensure_indexes_creates_all_four_indexes(mock_db):
    mock_db.articles.create_index = AsyncMock()
    asyncio.run(dbif.ensure_indexes())
    mock_db.articles.create_index.assert_has_calls(
        [
            call("hash"),
            call([("pubdate", pymongo.DESCENDING)], background=True),
            call([("summary", pymongo.TEXT)], background=True),
            call("pubname", background=True),
        ]
    )
