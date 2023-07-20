import pendulum
import pymongo
from bson.json_util import dumps
from ..config import readconf as rc

_host: str | None = None
_client: pymongo.MongoClient
_dbname: str | None = None


class ActuDBError(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__(value)


def get_db():
    global _client, _dbname
    # sanity check
    if _dbname is None:
        raise ActuDBError("DB name not defined. Must call init_db first.")
    return _client[_dbname]


def _init_db():
    global _host, _client, _dbname
    if _host is None or _dbname is None:  # not yet initialized, so read conf
        database = rc.get_conf_by_key("database")
        _host = database["url"]
        _dbname = database["dbname"]
        _client = pymongo.MongoClient(_host)
    db = get_db()
    db.articles.create_index("hash")
    db.articles.create_index([("pubdate", pymongo.DESCENDING)], background=True)
    db.articles.create_index([("summary", pymongo.TEXT)], background=True)
    db.articles.create_index("pubname", background=True)


def save_article(entry):
    db = get_db()
    db.articles.insert_one(entry)


def get_article_count() -> int:
    db = get_db()
    return db.articles.count_documents({})


def is_summary_in_db(target_hash, summary):
    db = get_db()
    articles_with_target_hash = db.articles.find({"hash": target_hash})
    for article in articles_with_target_hash:
        if article["summary"] == summary:
            return True
        else:
            continue
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
        {"pubdate": 1, "pubname": 1, "summary": 1, "title": 1},
    )


def make_tempdb_from_daterange(start, end):
    db = get_db()
    pipeline = [
        {"$match": {"pubdate": {"$gte": start, "$lte": end}}},
        {"$out": "daterange"},
    ]
    db.articles.aggregate(pipeline)
    db.daterange.create_index([("pubdate", pymongo.DESCENDING)])
    db.daterange.create_index([("summary", pymongo.TEXT)])


def today_range():
    return pendulum.today(), pendulum.tomorrow()


def get_articles_in_daterange(pubnames: list[str]):
    db = get_db()
    return db.daterange.find(
        {"pubname": {"$in": pubnames}},
        {"pubdate": 1, "pubname": 1, "summary": 1, "title": 1},
    ).sort("pubdate", 1)


def cursor_to_json(cursor):
    return dumps(cursor)


# call on load to initialize db
_init_db()
