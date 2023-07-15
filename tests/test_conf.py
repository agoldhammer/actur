from actur.config import readconf
from actur.utils import dbif, feeds

import pytest


@pytest.fixture(autouse=True, scope="module")
def setup():
    dbif.init_db()
    yield


def test_config_and_feedparsing():
    # test setting of database
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
