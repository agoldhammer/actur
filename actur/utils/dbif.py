import pendulum
import pymongo
from bson.json_util import RELAXED_JSON_OPTIONS, dumps
from pymongo import AsyncMongoClient

from actur.config import readconf as rc
from actur.utils import hasher

_host: str | None = None
_client: AsyncMongoClient | None = None
_dbname: str | None = None


class ActuDBError(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__(value)


def get_db():
    global _client, _dbname
    if _dbname is None:
        raise ActuDBError("DB name not defined. Must call init_db first.")
    return _client[_dbname] # type: ignore


def init_db():
    global _host, _client, _dbname
    try:
        database = rc.get_conf_by_key("database")
        _host = database["url"]
        _dbname = database["dbname"]
        _client = AsyncMongoClient(_host)
    
    except Exception as e:
        raise ActuDBError(f"Error initializing database: {e}")


async def ensure_indexes():
    db = get_db()
    await db.articles.create_index("hash")
    await db.articles.create_index([("pubdate", pymongo.DESCENDING)], background=True)
    await db.articles.create_index([("summary", pymongo.TEXT)], background=True)
    await db.articles.create_index("pubname", background=True)


async def save_article(entry):
    db = get_db()
    await db.articles.insert_one(entry)


async def get_article_count() -> int:
    db = get_db()
    return await db.articles.count_documents({})


async def is_summary_in_db(target_hash, normalized_summary):
    db = get_db()
    async for article in db.articles.find({"hash": target_hash}):
        if hasher.normalize_summary(article["summary"]) == normalized_summary:
            return True
    return False


def find_text(collname: str, search_text: str):
    db = get_db()
    return db[collname].find({"$text": {"$search": search_text}}).sort("pubdate", 1)


def find_articles_by_pubname(pubname: str):
    db = get_db()
    return db.articles.find({"pubname": pubname}, {"pubdate": 1})


def find_articles_by_daterange(start, end):
    db = get_db()
    return db.articles.find(
        {"pubdate": {"$gte": start, "$lte": end}},
        {"pubdate": 1, "pubname": 1, "summary": 1, "title": 1, "cat": 1},
    )


async def make_tempdb_from_daterange(start, end):
    db = get_db()
    pipeline = [
        {"$match": {"pubdate": {"$gte": start, "$lte": end}}},
        {"$out": "daterange"},
    ]
    cursor = await db.articles.aggregate(pipeline)
    await cursor.to_list(length=None)
    await db.daterange.create_index([("pubdate", pymongo.DESCENDING)])
    await db.daterange.create_index([("summary", pymongo.TEXT)])


def today_range():
    return pendulum.today(), pendulum.tomorrow()


def get_articles_in_daterange(pubnames: list[str]):
    db = get_db()
    return db.daterange.find(
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
    ).sort("pubdate", 1)


def cursor_to_json(cursor):
    return dumps(cursor, json_options=RELAXED_JSON_OPTIONS)


def get_uncategorized_articles():
    db = get_db()
    return db.articles.find(
        {"$or": [{"cat": {"$exists": False}}, {"cat": "uncategorized"}]},
        {"_id": 1, "title": 1},
    )


async def update_article_cat(article_id, category: str):
    db = get_db()
    await db.articles.update_one({"_id": article_id}, {"$set": {"cat": category}})


async def test_for_cat():
    db = get_db()
    async for article in db.articles.find():
        print(article.get("cat", "FAIL!"))


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_for_cat())
