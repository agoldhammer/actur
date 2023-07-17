import pytest

from actur.utils import dbif


@pytest.fixture(autouse=True, scope="module")
def setup():
    dbif.init_db()
    yield


def test_count():
    count = dbif.get_article_count()
    assert count > 0  # nosec


def test_already_in():
    db = dbif.get_db()
    art = db.articles.find_one()
    h = s = ""
    if art is not None:
        h = art["hash"]
        s = art["summary"]
    is_in = dbif.is_summary_in_db(h, s)
    assert is_in  # nosec B101
    # test with different hash
    is_in = dbif.is_summary_in_db("abc", s)
    # test with different summary
    assert not is_in  # nosec B101
    is_in = dbif.is_summary_in_db(h, "abc")
    assert not is_in  # nosec B101
