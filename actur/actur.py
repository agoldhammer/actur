"""Main module."""
import feedparser
import pprint

d = feedparser.parse("https://feedparser.readthedocs.io/en/latest/examples/atom10.xml")
# print(d)
print(d["feed"]["title"])
print(d["feed"]["updated"])
pprint.pprint(d)
