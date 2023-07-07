import pymongo

_host = ""


def init_db(host: str):
    global _host
    _host = host


def db_setup():
    global _host
    _client = pymongo.MongoClient(_host)
    _client.actur.articles.create_index("hash")

    def save_article(entry):
        _client.actur.articles.insert_one(entry)

    def is_summary_in_db(target_hash, summary):
        print("checking hash", target_hash, type(target_hash))
        articles_with_target_hash = _client.actur.articles.find({"hash": target_hash})
        print("found:", len(list(articles_with_target_hash)))
        articles_with_target_hash = _client.actur.articles.find({"hash": target_hash})
        # articles_with_hash = _client.actur.articles.find()
        for article in articles_with_target_hash:
            print("dup hash found", article["hash"], article["_id"])
            print(article["summary"], "\nxxxxxxxxx\n", summary)
            if article["summary"] == summary:
                print("dup article found with hash", target_hash)
                return True
            else:
                print("text differs")
                continue
        return False

    return save_article, is_summary_in_db


if __name__ == "__main__":
    init_db("mongodb://elite.local")
    save_art, check_exist = db_setup()
    exists = check_exist(8526757651552039682, "dummy")
    exists = check_exist(7822652997085437942, "dummy")
    exists = check_exist(1201890604943332644, "dummy")
    exists = check_exist(-964779573267868267, "dummy")
    print("exists?", exists)
