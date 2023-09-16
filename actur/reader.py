import datetime
import logging
import os
import time

import feedparser

from actur.config import readconf as rc
from actur.utils import dbif, feeds, hasher

_total_processed: int = 0
_total_added: int = 0
_total_skipped: int = 0
_logger: logging.Logger


def setup_logging():
    global _logger
    LOGFILEPATH = rc.get_conf_by_key("logfilepath")["path"]
    if not os.access(LOGFILEPATH, os.W_OK):
        raise Exception(f"Logfile {LOGFILEPATH} does not exist or is not writable")
    _logger = logging.getLogger("actu-rdr-log")
    _logger.setLevel(logging.INFO)
    fh = logging.FileHandler(LOGFILEPATH)
    fh.setLevel(logging.INFO)
    myformat = logging.Formatter("%(asctime)s-%(name)s:%(levelname)s--%(message)s")
    logging.Formatter.converter = time.gmtime
    fh.setFormatter(myformat)
    _logger.addHandler(fh)


def pcounters():
    n_processed = 0
    n_added = 0
    n_skipped = 0

    def bump_processed():
        nonlocal n_processed
        global _total_processed
        n_processed += 1
        _total_processed += 1

    def bump_added():
        global _total_added
        nonlocal n_added
        n_added = n_added + 1
        _total_added += 1

    def bump_skipped():
        global _total_skipped
        nonlocal n_skipped
        n_skipped = n_skipped + 1
        _total_skipped += 1

    def counts2str():
        return f"Processed: {n_processed}, Added: {n_added}, Skipped: {n_skipped}"

    return bump_processed, bump_added, bump_skipped, counts2str


def process_feed(feed: feeds.Feed, pubname: str, silent: bool):
    """read, parse, and store one feed

    Args:
        feed (feeds.Feed): a Feed descriptor
        pubname (str): publication generating feed
    """
    bump_processed, bump_added, bump_skipped, get_counts = pcounters()
    feedname = feed.name
    url = feed.url
    d = feedparser.parse(url)
    if not silent:
        print(f"+++\nFeed: {feedname}")
        print(20 * "_")
        print("Version:", d.version)
        if d.bozo:
            print("XML is ill-formed")
        print("Status:", d.status)
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
    if not silent:
        print(get_counts())


def parse_pub(pub: feeds.Publication, silent: bool):
    if not silent:
        print("\nPublication:", pub.name)
        print(20 * "*")
    for feed in pub.feeds:
        process_feed(feed, pub.name, silent)
    if not silent:
        print(f"Done with pub {pub.name}\n")
        print(20 * "*")


def process_pubs(xgroup: str | None, silent: bool, no_logging: bool):
    """parse feed for pubs

    Args:
        xgroup (str | None): if group specified, exclude from read_
    """
    global _total_added, _total_processed, _total_skipped, _logger
    _total_added = _total_processed = _total_skipped = 0
    msg = ""

    pubs = feeds.get_publications()
    if xgroup is not None:
        pubs = [pub for pub in pubs if pub.group != xgroup]

    for pub in pubs:
        parse_pub(pub, silent)
    ndocs = dbif.get_article_count()
    msg = f"Tot: {_total_processed}, Added: {_total_added}, Skipped: {_total_skipped}. # of docs in db: {ndocs}"  # noqa
    if not silent:
        print(msg)
    if not no_logging:
        _logger.info(msg)


def main():
    # process_pubs(None)
    pass


if __name__ == "__main__":
    main()
