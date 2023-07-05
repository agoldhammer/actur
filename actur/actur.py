"""Main module."""
import feedparser

import pprint

from feeds import lemonde, sz, corriere

print(lemonde, corriere, sz)

current_feed = lemonde

name = current_feed.name
feed = current_feed.feeds[0]
feedname = feed.name
url = feed.url

d = feedparser.parse(url)
print("version", d.version)
print("bozo/status", d.bozo, d.status)
# print(d)
# print(d["feed"]["title"])
# print(d["feed"]["updated"])
# print(d.feed.title)
print("Pubname", name)
print("Feed:", feedname)
# print("channel title", d.feed.keys())
# print("d.channel", d.channel.keys())
# pprint.pprint(d)
print("d keys", d.keys())
print("no. entries", len(d.entries))
for entry in d.entries:
    # pprint.pprint(entry)
    # print("author", entry.author)
    print("date", entry.published)
    print("link", entry.link)
    print("summary", entry.summary)
    print("----------------\n")
    # print(entry.link)
    # print(entry.summary)

# print("channel by items")
# print("channel title", d.channel.title)
# for item in d.channel.items():
#     pprint.pprint(item)
# print("channel links\n")
# pprint.pprint(d.channel.links)
# print("namespaces", d.namespaces)
# print("feedkeys")
# pprint.pprint(d.feed.keys())
# print("feed links", d.feed.links)
# print("feed summary", d.feed.summary)
# print(d.updated)
# print(d.channel.description)
