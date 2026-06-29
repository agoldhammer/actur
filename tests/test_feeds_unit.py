"""Unit tests for actur.utils.feeds — no live config or DB required."""

from unittest.mock import patch
import pytest

from actur.utils.feeds import Feed, Publication, make_feed, make_pub, get_publications


# ---------------------------------------------------------------------------
# Feed dataclass
# ---------------------------------------------------------------------------


def test_feed_stores_name_and_url():
    f = Feed(name="reuters", url="https://example.com/feed")
    assert f.name == "reuters"
    assert f.url == "https://example.com/feed"


def test_feed_equality():
    assert Feed("reuters", "https://a.com") == Feed("reuters", "https://a.com")
    assert Feed("reuters", "https://a.com") != Feed("reuters", "https://b.com")


def test_feed_repr_contains_fields():
    r = repr(Feed("reuters", "https://a.com"))
    assert "reuters" in r
    assert "https://a.com" in r


# ---------------------------------------------------------------------------
# Publication dataclass
# ---------------------------------------------------------------------------


def test_publication_stores_fields():
    feeds = [Feed("f1", "https://a.com"), Feed("f2", "https://b.com")]
    pub = Publication(name="Reuters", group="news", feeds=feeds)
    assert pub.name == "Reuters"
    assert pub.group == "news"
    assert pub.feeds == feeds


def test_publication_equality():
    f = Feed("f", "https://a.com")
    assert Publication("R", "news", [f]) == Publication("R", "news", [f])
    assert Publication("R", "news", [f]) != Publication("X", "news", [f])


def test_publication_with_empty_feeds():
    pub = Publication(name="Empty", group="test", feeds=[])
    assert pub.feeds == []


# ---------------------------------------------------------------------------
# make_feed
# ---------------------------------------------------------------------------


def test_make_feed_returns_feed():
    f = make_feed(["ap-wire", "https://ap.com/rss"])
    assert isinstance(f, Feed)
    assert f.name == "ap-wire"
    assert f.url == "https://ap.com/rss"


def test_make_feed_uses_index_zero_as_name_and_one_as_url():
    f = make_feed(["name-part", "url-part"])
    assert f.name == "name-part"
    assert f.url == "url-part"


# ---------------------------------------------------------------------------
# make_pub
# ---------------------------------------------------------------------------


def test_make_pub_returns_publication():
    raw = [["feed-a", "https://a.com"], ["feed-b", "https://b.com"]]
    pub = make_pub("MyPub", "mygroup", raw)
    assert isinstance(pub, Publication)
    assert pub.name == "MyPub"
    assert pub.group == "mygroup"


def test_make_pub_converts_rawfeeds_to_feed_objects():
    raw = [["feed-a", "https://a.com"], ["feed-b", "https://b.com"]]
    pub = make_pub("MyPub", "mygroup", raw)
    assert len(pub.feeds) == 2
    assert all(isinstance(f, Feed) for f in pub.feeds)
    assert pub.feeds[0] == Feed("feed-a", "https://a.com")
    assert pub.feeds[1] == Feed("feed-b", "https://b.com")


def test_make_pub_with_no_feeds():
    pub = make_pub("EmptyPub", "g", [])
    assert pub.feeds == []


def test_make_pub_with_single_feed():
    pub = make_pub("SinglePub", "g", [["only", "https://only.com"]])
    assert len(pub.feeds) == 1
    assert pub.feeds[0].name == "only"


# ---------------------------------------------------------------------------
# get_publications
# ---------------------------------------------------------------------------

_RAW_PUBS = [
    {
        "name": "Reuters",
        "group": "english",
        "feeds": [["reuters-top", "https://reuters.com/rss"], ["reuters-world", "https://reuters.com/world"]],
    },
    {
        "name": "LeMonde",
        "group": "french",
        "feeds": [["lemonde-fr", "https://lemonde.fr/rss"]],
    },
]


def test_get_publications_returns_list_of_publications():
    with patch("actur.utils.feeds.rc.get_conf_by_key", return_value=_RAW_PUBS):
        result = get_publications()
    assert isinstance(result, list)
    assert all(isinstance(p, Publication) for p in result)


def test_get_publications_returns_correct_count():
    with patch("actur.utils.feeds.rc.get_conf_by_key", return_value=_RAW_PUBS):
        result = get_publications()
    assert len(result) == 2


def test_get_publications_maps_name_and_group():
    with patch("actur.utils.feeds.rc.get_conf_by_key", return_value=_RAW_PUBS):
        result = get_publications()
    assert result[0].name == "Reuters"
    assert result[0].group == "english"
    assert result[1].name == "LeMonde"
    assert result[1].group == "french"


def test_get_publications_maps_feeds():
    with patch("actur.utils.feeds.rc.get_conf_by_key", return_value=_RAW_PUBS):
        result = get_publications()
    assert len(result[0].feeds) == 2
    assert result[0].feeds[0] == Feed("reuters-top", "https://reuters.com/rss")
    assert result[0].feeds[1] == Feed("reuters-world", "https://reuters.com/world")
    assert len(result[1].feeds) == 1
    assert result[1].feeds[0] == Feed("lemonde-fr", "https://lemonde.fr/rss")


def test_get_publications_queries_correct_key():
    with patch("actur.utils.feeds.rc.get_conf_by_key", return_value=_RAW_PUBS) as mock_get:
        get_publications()
    mock_get.assert_called_once_with("Publications")


def test_get_publications_returns_empty_list_when_no_pubs():
    with patch("actur.utils.feeds.rc.get_conf_by_key", return_value=[]):
        result = get_publications()
    assert result == []


def test_get_publications_propagates_config_error():
    with patch("actur.utils.feeds.rc.get_conf_by_key", side_effect=Exception("no config")):
        with pytest.raises(Exception, match="no config"):
            get_publications()
