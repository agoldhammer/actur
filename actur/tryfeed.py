# try out a new feed

import feedparser
import pprint
import sys


def main(url: str):
    d = feedparser.parse(url)
    print(f"Feed title: {d.feed.title}")
    for entry in d.entries:
        pprint.pprint(entry)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://www.liberation.fr/arc/outboundfeeds/rss-all/?outputType=xml"
    main(url)

"""
https://newsfeed.zeit.de/index
https://faz.net/rss/aktuel
https://www.handelsblatt.com/contentexport/feed/top-themen
https://services.lesechos.fr/rss/les-echos-idees.xml
https://services.lesechos.fr/rss/les-echos-economie.xml
https://services.lesechos.fr/rss/les-echos-finance-marches.xml

"""
