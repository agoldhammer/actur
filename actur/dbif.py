import pendulum
import pymongo

_host: str = ""
_client: pymongo.MongoClient
_dbname: str = ""


def get_db():
    global _client, _dbname
    return _client[_dbname]


def init_db(host: str, dbname: str = "actur"):
    global _host, _client, _dbname
    _host = host
    _dbname = dbname
    _client = pymongo.MongoClient(_host)
    db = get_db()
    db.articles.create_index("hash")
    db.articles.create_index([("pubdate", pymongo.DESCENDING)], background=True)
    db.articles.create_index([("summary", pymongo.TEXT)], background=True)
    db.articles.create_index("pubname", background=True)


def save_article(entry):
    db = get_db()
    db.articles.insert_one(entry)


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


def find_text(search_text: str):
    db = get_db()
    return db.articles.find({"$text": {"$search": search_text}})


def find_articles_by_pubname(pubname: str):
    db = get_db()
    return db.articles.find({"pubname": pubname}, {"pubdate": 1})


def find_articles_by_daterange(start, end):
    db = get_db()
    return db.articles.find(
        {"pubdate": {"$gte": start, "$lte": end}},
        {"pubdate": 1, "pubname": 1, "summary": 1, "title": 1},
    )


if __name__ == "__main__":
    init_db("mongodb://elite.local")
    cursor = find_text("émeute")
    for article in cursor:
        print(article)
    cursor = find_articles_by_pubname("SZ")
    for article in cursor:
        print(article)
    start = pendulum.yesterday()
    end = pendulum.today()
    cursor = find_articles_by_daterange(start, end)
    for article in cursor:
        print(article)
    start = pendulum.today()
    end = pendulum.tomorrow()
    # cursor = find_articles_by_daterange(start, end)
    # for article in cursor:
    #     print(article)
    print("\nsorting")
    cursor = find_articles_by_daterange(start, end).sort(
        [("pubname", 1), ("pubdate", 1)]
    )
    for article in cursor:
        print(f"{article['pubname']}: {article['pubdate']}")
        print(article["title"])
