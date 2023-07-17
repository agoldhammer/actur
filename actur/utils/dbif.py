import pendulum
import pymongo
from . import display
from ..config import readconf as rc

_host: str | None = None
_client: pymongo.MongoClient
_dbname: str = ""
# _default_host = "mongodb://192.168.0.128"


class ActuDBError(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__(value)


def get_db():
    global _client, _dbname
    # sanity check
    if _dbname == "":
        raise ActuDBError("DB name not defined. Must call init_db first.")
    return _client[_dbname]


def init_db():
    global _host, _client, _dbname
    if _host is None:  # not yet initialized, so read conf
        rc.read_conf()
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
    # print("checking hash", target_hash)
    articles_with_target_hash = db.articles.find({"hash": target_hash})
    # articles_with_hash = _client.actur.articles.find()
    for article in articles_with_target_hash:
        # print("dup hash found", article["hash"], article["_id"])
        # print(article["summary"], "\nxxxxxxxxx\n", summary)
        if article["summary"] == summary:
            # print("dup article found with hash", target_hash)
            return True
        else:
            # print("text differs")
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
    return db.daterange.find({"pubname": {"$in": pubnames}}).sort("pubdate", 1)


# ! For testing only!!
def view_past_day():
    init_db()

    start = pendulum.today()
    end = pendulum.tomorrow()

    print("\nsorting")
    cursor = find_articles_by_daterange(start, end).sort(
        [("pubname", 1), ("pubdate", -1)]
    )
    for article in cursor:
        # print(f"{article['pubname']}: {article['pubdate']}")
        # print(article["title"])
        display.display_article(article, summary_flag=True)
