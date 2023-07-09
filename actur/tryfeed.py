# try out a new feed

import feedparser
import pprint


def main(url: str):
    d = feedparser.parse(url)
    pprint.pprint(d)


if __name__ == "__main__":
    main("https://www.liberation.fr/arc/outboundfeeds/rss-all/?outputType=xml")
