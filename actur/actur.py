import datetime

import dbif
import feedparser
import feeds
import hasher


def pcounters():
    n_processed = 0
    n_added = 0
    n_skipped = 0

    def bump_processed():
        nonlocal n_processed
        n_processed += 1

    def bump_added():
        nonlocal n_added
        n_added = n_added + 1

    def bump_skipped():
        nonlocal n_skipped
        n_skipped = n_skipped + 1

    def counts2str():
        return f"Processed: {n_processed}, Added: {n_added}, Skipped: {n_skipped}"

    return bump_processed, bump_added, bump_skipped, counts2str


def process_feed(feed: feeds.Feed, pubname: str):
    bump_processed, bump_added, bump_skipped, get_counts = pcounters()
    feedname = feed.name
    url = feed.url
    print("Feed:", feedname)
    print(20 * "_")
    d = feedparser.parse(url)
    # TODO: Should d.feed.title be stored instead of feed.name?
    print("Feed title:", d.feed.title)
    print("Version:", d.version)
    print("bozo/status", d.bozo, d.status)
    # print("d keys", d.keys())
    print("no. entries", len(d.entries))
    for entry in d.entries:
        bump_processed()
        dt = datetime.datetime(*entry.published_parsed[:6])
        entry["pubdate"] = dt
        ehash = hasher.ag_hash(entry.summary)
        entry["hash"] = ehash
        already_in = dbif.is_summary_in_db(ehash, entry.summary)
        if already_in:
            bump_skipped()
        else:
            entry.pop("summary_detail", "")
            entry.pop("guidislink", "")
            entry.pop("media_credit", "")
            entry["pubname"] = pubname
            entry["feedname"] = feedname
            dbif.save_article(entry)
            bump_added()
    print(get_counts())


def parse_pub(pub: feeds.Publication):
    print("Publication:", pub.name)
    print(20 * "*")
    for feed in pub.feeds:
        process_feed(feed, pub.name)
    print(f"Done with pub {pub.name}\n")


def process_pubs():
    for pub in feeds.get_papers():
        parse_pub(pub)


def main():
    dbif.init_db("mongodb://elite.local")
    process_pubs()


if __name__ == "__main__":
    main()
