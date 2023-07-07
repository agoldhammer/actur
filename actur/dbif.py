import pymongo

_host = ""


def init_db(host: str):
    global _host
    _host = host


def save_article_fn():
    global _host
    _client = pymongo.MongoClient(_host)

    def save_article(entry):
        _client.actur.articles.insert_one(entry)

    return save_article


if __name__ == "__main__":
    init_db("mongodb://elite.local")
    print(_host)
