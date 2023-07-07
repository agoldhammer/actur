import datetime

# import pprint

# from textwrap import TextWrapper
import dbif
import feedparser
import feeds

# import pprint


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
    n_processed = 0
    n_skipped = 0
    n_saved = 0
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
        n_processed += 1
        # pprint.pprint(entry)

        # print("type:", type(entry))
        print("keys:", entry.keys())
        # print("id: ", entry.id)
        # print("title:", entry.title)
        # print("title detail:", entry.title_detail)
        # print("media cotennt:", entry.media_content)
        # print("credit:", entry.credit)
        # print("media credit:", entry.media_credit)
        # print("author", entry.author)
        # print("date:", entry.published, entry.published_parsed)
        dt = datetime.datetime(*entry.published_parsed[:6])
        entry["pubdate"] = dt
        print("dt", dt)
        # print("link:", entry.link)
        # print("links:", entry.links)
        # wrapper = TextWrapper(
        #     width=70, initial_indent="+--->", subsequent_indent="    "
        # )
        # print(wrapper.fill(f"summary: {entry.summary}"))
        # print("summary detail:", entry.summary_detail)
        ehash = hash(entry.summary)
        entry["hash"] = ehash
        # print("hash:", entry.hash)
        add_new_hash(ehash)
        print("ENTRY:---------->")
        # pprint.pprint(entry)
        # # save to database
        already_in = is_summary_in_db(ehash, entry.summary)
        if already_in:
            print("skipping")
            n_skipped += 1
        else:
            save_article(entry)
            n_saved += 1
            print("entry saved")
        print("END ENTRY----------------\n")
    print(f"Processed: {n_processed}, Saved: {n_saved}, Skipped: {n_skipped}")


def parse_pub(pub: feeds.Publication):
    print("Publication:", pub.name)
    print("**********")
    for feed in pub.feeds:
        process_feed(feed)
    view_duped_hashes()
    # feed = pub.feeds[0]  # do only first feed

    # print(entry.link)
    # print(entry.summary)


def process_pubs():
    for pub in feeds.get_papers():
        parse_pub(pub)


def main():
    dbif.init_db("mongodb://elite.local")
    process_pubs()


if __name__ == "__main__":
    main()
