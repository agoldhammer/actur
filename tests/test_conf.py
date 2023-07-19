from actur.config import readconf
from actur.utils import dbif, feeds
import feedparser

import pytest


# @pytest.fixture(autouse=True, scope="module")
# def setup():
#     # dbif.init_db()
#     yield


def test_config_and_feedparsing():
    # test setting of database
    _ = dbif.get_db()  # needed to initialize the db
    res = readconf.get_conf_by_key("database")
    assert "dbname" in res  # nosec
    assert "url" in res  # nosec
    # test that Publication dataclasses are returned
    rawpubs = readconf.get_conf_by_key("Publications")
    names = [pub["name"] for pub in rawpubs]
    assert "LeMonde" in names  # nosec
    #  test transformation of rawpubs into Publication dataclasses
    pubs = feeds.get_publications()
    names = [pub.name for pub in pubs]
    assert "SZ" in names  # nosec


# ensure that every configured feed can read its url
# ! This test is slow, so omit from coverage
@pytest.mark.no_cover
def test_feeds():
    pubs = feeds.get_publications()
    for pub in pubs:
        print("connecting to pub.name")
        for feed in pub.feeds:
            print(f"connecting to feed {feed.name}")
            d = feedparser.parse(feed.url)
            assert d is not None  # nosec
            assert d.entries is not None  # nosec
            for entry in d.entries:
                assert entry.published is not None  # nosec
