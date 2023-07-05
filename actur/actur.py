"""Main module."""
import feedparser

# import pprint

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
