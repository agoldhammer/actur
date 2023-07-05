import feedparser

# import pprint

import feeds
from typing import Type


def parse_pub(pub: Type[feeds.Publication]):
    pubname = pub.name
    feed = pub.feeds[0]  # do only first feed
    feedname = feed.name
    url = feed.url
    print("Pubname", pubname)
    print("Feed:", feedname)
    d = feedparser.parse(url)
    print("version", d.version)
    print("bozo/status", d.bozo, d.status)
    # print("d keys", d.keys())
    print("no. entries", len(d.entries))
    for entry in d.entries:
        # pprint.pprint(entry)
        print("id", entry.id)
        # print("author", entry.author)
        print("date", entry.published)
        print("link", entry.link)
        print("summary", entry.summary)
        print("----------------\n")
        # print(entry.link)
        # print(entry.summary)


for pub in feeds.get_papers():
    parse_pub(pub)
