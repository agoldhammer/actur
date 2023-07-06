import feedparser

# import pprint

import feeds


def process_feed(feed: feeds.Feed):
    feedname = feed.name
    url = feed.url
    print("Feed:", feedname)
    print("&&&&&&&&&&&&&&&&&")
    d = feedparser.parse(url)
    print("version", d.version)
    print("bozo/status", d.bozo, d.status)
    # print("d keys", d.keys())
    print("no. entries", len(d.entries))
    for entry in d.entries:
        # pprint.pprint(entry)
        print("type:", type(entry))
        print("keys:", entry.keys())
        print("id", entry.id)
        # print("author", entry.author)
        print("date:", entry.published, entry.published_parsed)
        print("link:", entry.link)
        print("links:", entry.links)
        print("summary:", entry.summary)
        print("hash:", hash(entry.summary))
        print("----------------\n")


def parse_pub(pub: feeds.Publication):
    print("Publication:", pub.name)
    print("**********")
    for feed in pub.feeds:
        process_feed(feed)
    # feed = pub.feeds[0]  # do only first feed

    # print(entry.link)
    # print(entry.summary)


for pub in feeds.get_papers():
    parse_pub(pub)
