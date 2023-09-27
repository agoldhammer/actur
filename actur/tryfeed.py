# try out a new feed

import feedparser
import pprint
import sys


def main(url: str):
    d = feedparser.parse(url)
    print("feed keys", d.feed.keys())
    if "title" in d.feed:
        print(f"Feed title: {d.feed.title}")
    for entry in d.entries:
        pprint.pprint(entry)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = (
            "https://www.ft.com/myft/following/126e6584-dcdf-4320-9a28-2c4a614e7c0c.rss"
        )
    main(url)

"""
https://newsfeed.zeit.de/index
https://faz.net/rss/aktuel
https://www.handelsblatt.com/contentexport/feed/top-themen
https://services.lesechos.fr/rss/les-echos-idees.xml
https://services.lesechos.fr/rss/les-echos-economie.xml
https://services.lesechos.fr/rss/les-echos-finance-marches.xml

"""
