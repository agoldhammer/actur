import datetime

import feedparser
from actur.utils import dbif, feeds, hasher

_total_processed: int = 0
_total_added: int = 0
_total_skipped: int = 0


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
    global _total_processed, _total_added, _total_skipped
    bump_processed, bump_added, bump_skipped, get_counts = pcounters()
    feedname = feed.name
    url = feed.url
    print("Feed:", feedname)
    print(20 * "_")
    d = feedparser.parse(url)
    # !: Should d.feed.title be stored instead of feed.name?
    # ! NO, b/c Some feeds seem to have no attr title
    # print("Feed title:", d.feed.title)
    print("Version:", d.version)
    if d.bozo:
        print("XML is ill-formed")
    print("Status:", d.status)
    print("no. entries", len(d.entries))
    for entry in d.entries:
        bump_processed()
        _total_processed += 1
        dt = datetime.datetime(*entry.published_parsed[:6])
        entry["pubdate"] = dt
        ehash = hasher.ag_hash(entry.summary)
        entry["hash"] = ehash
        already_in = dbif.is_summary_in_db(ehash, entry.summary)
        if already_in:
            bump_skipped()
            _total_skipped += 1
        else:
            entry.pop("summary_detail", "")
            entry.pop("guidislink", "")
            entry.pop("media_credit", "")
            entry["pubname"] = pubname
            entry["feedname"] = feedname
            dbif.save_article(entry)
            bump_added()
            _total_added += 1
    print(get_counts())


def parse_pub(pub: feeds.Publication):
    print("\nPublication:", pub.name)
    print(20 * "*")
    for feed in pub.feeds:
        process_feed(feed, pub.name)
    print(f"Done with pub {pub.name}\n")
    print(20 * "*")


def process_pubs():
    global _total_added, _total_processed, _total_skipped
    _total_processed = _total_added = _total_skipped = 0
    for pub in feeds.get_publications():
        parse_pub(pub)
    ndocs = dbif.get_article_count()
    print(f"Read complete. No. docs in db: {ndocs}")
    print(
        f"Processed: {_total_processed}, Added: {_total_added}, Skipped: {_total_skipped}"
    )


def main():
    dbif.init_db()
    process_pubs()


if __name__ == "__main__":
    main()
