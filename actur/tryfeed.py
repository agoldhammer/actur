# try out a new feed

import sys

import feedparser


def main(url: str):
    d = feedparser.parse(url)
    if d.bozo:
        print(f"bozo {d.bozo} error {d.bozo_exception}")
    print("feed keys", d.feed.keys())  # type: ignore
    if "summary" in d.feed:
        print(f"Feed summary: {d.feed.summary}")  # type: ignore
    if "title" in d.feed:
        print(f"Feed title: {d.feed.title}")  # type: ignore
    for entry in d.entries:
        print(
            f"entry.title: {entry.title}\n  entry.summary: {entry.summary}\n  entry.published: {entry.published}\n  entry.pubname: {entry.link}\n\n"
        )  # type: ignore


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "http://xml2.corriereobjects.it/feed-hp/homepage.xml"
    main(url)

"""
https://newsfeed.zeit.de/index
https://faz.net/rss/aktuel
https://www.handelsblatt.com/contentexport/feed/top-themen
https://services.lesechos.fr/rss/les-echos-idees.xml
https://services.lesechos.fr/rss/les-echos-economie.xml
https://services.lesechos.fr/rss/les-echos-finance-marches.xml

"""
