import pymongo

_host: str = ""
_client: pymongo.MongoClient


def init_db(host: str):
    global _host, _client
    _host = host
    _client = pymongo.MongoClient(_host)
    _client.actur.articles.create_index("hash")
    _client.actur.articles.create_index(
        [("pubdate", pymongo.DESCENDING)], background=True
    )
    _client.actur.articles.create_index([("summary", pymongo.TEXT)], background=True)


def save_article(entry):
    global _client
    _client.actur.articles.insert_one(entry)


def is_summary_in_db(target_hash, summary):
    global _client
    # print("checking hash", target_hash)
    articles_with_target_hash = _client.actur.articles.find({"hash": target_hash})
    # print("found:", len(list(articles_with_target_hash)))
    articles_with_target_hash = _client.actur.articles.find({"hash": target_hash})
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

    # return save_article, is_summary_in_db


if __name__ == "__main__":
    init_db("mongodb://elite.local")
