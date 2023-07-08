import datetime

# import pprint

# from textwrap import TextWrapper
import dbif
import feedparser
import feeds
import hasher

# import pprint


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


def process_feed(feed: feeds.Feed):
    bump_processed, bump_added, bump_skipped, get_counts = pcounters()
    feedname = feed.name
    url = feed.url
    print("Feed:", feedname)
    print("&&&&&&&&&&&&&&&&&")
    d = feedparser.parse(url)
    print("version", d.version)
    print("bozo/status", d.bozo, d.status)
    # print("d keys", d.keys())
    print("no. entries", len(d.entries))
    save_article, is_summary_in_db = dbif.db_setup()
    for entry in d.entries:
        bump_processed()
        # print("keys:", entry.keys())
        dt = datetime.datetime(*entry.published_parsed[:6])
        entry["pubdate"] = dt
        # print("dt", dt)
        ehash = hasher.ag_hash(entry.summary)
        # print("ehash: ", ehash)
        entry["hash"] = ehash
        # print("ENTRY:---------->")
        already_in = is_summary_in_db(ehash, entry.summary)
        if already_in:
            # print("skipping")
            bump_skipped()
        else:
            # entry.pop("summary_detail")
            # entry.pop("guidislink")
            # entry.pop("media_credit")
            save_article(entry)
            bump_added()
            # print("entry saved")
        # print("END ENTRY----------------\n")
    print(get_counts())


def parse_pub(pub: feeds.Publication):
    print("Publication:", pub.name)
    print("**********")
    for feed in pub.feeds:
        process_feed(feed)


def process_pubs():
    for pub in feeds.get_papers():
        parse_pub(pub)


def main():
    dbif.init_db("mongodb://elite.local")
    process_pubs()


if __name__ == "__main__":
    main()
