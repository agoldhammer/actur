import pymongo

host = "mongodb://elite.local"
client = pymongo.MongoClient(host)
db = client.actur
feeds = db.feeds
print(host, client, db, feeds)
artid = feeds.insert_one({"author": "Art"}).inserted_id
print(artid)
