import asyncio

from actur.utils import dbif


def test_count():
    count = asyncio.run(dbif.get_article_count())
    assert count > 0  # nosec


def test_already_in():
    async def _test():
        db = dbif.get_db()
        art = await db.articles.find_one()
        h = s = ""
        if art is not None:
            h = art["hash"]
            s = art["summary"]
        is_in = await dbif.is_summary_in_db(h, s)
        assert is_in  # nosec B101
        is_in = await dbif.is_summary_in_db("abc", s)
        assert not is_in  # nosec B101
        is_in = await dbif.is_summary_in_db(h, "abc")
        assert not is_in  # nosec B101

    asyncio.run(_test())
