import feedparser

# import pprint

import feeds
from textwrap import TextWrapper


def check_hash():
    hashes_seen = []
    hashes_duped = []

    def add_hash(newhash):
        if newhash in hashes_seen:
            hashes_duped.append(newhash)
        else:
            hashes_seen.append(newhash)

    def view_dupes():
        print("+++no. hashes recorded:", len(hashes_seen))
        nduped = len(hashes_duped)
        if nduped > 0:
            print("no. duped hashes:", nduped)
            print("duped hashes:", hashes_duped)
        else:
            print("No duped hashes")

    return add_hash, view_dupes


add_new_hash, view_duped_hashes = check_hash()


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
        print("id: ", entry.id)
        print("title:", entry.title)
        print("title detail:", entry.title_detail)
        # print("media cotennt:", entry.media_content)
        # print("credit:", entry.credit)
        # print("media credit:", entry.media_credit)
        # print("author", entry.author)
        print("date:", entry.published, entry.published_parsed)
        print("link:", entry.link)
        print("links:", entry.links)
        wrapper = TextWrapper(
            width=70, initial_indent="+--->", subsequent_indent="    "
        )
        print(wrapper.fill(f"summary: {entry.summary}"))
        print("summary detail:", entry.summary_detail)
        ehash = hash(entry.summary)
        print("hash:", ehash)
        add_new_hash(ehash)
        print("----------------\n")


def parse_pub(pub: feeds.Publication):
    print("Publication:", pub.name)
    print("**********")
    for feed in pub.feeds:
        process_feed(feed)
    view_duped_hashes()
    # feed = pub.feeds[0]  # do only first feed

    # print(entry.link)
    # print(entry.summary)


for pub in feeds.get_papers():
    parse_pub(pub)
