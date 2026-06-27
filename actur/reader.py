import asyncio
import datetime
import logging
import os
import time

import feedparser

from actur.categorize import classify_by_title
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


async def process_feed(
    feed: feeds.Feed,
    pubname: str,
    silent: bool,
    no_logging: bool,
    categorize: bool,
    no_store: bool = False,
) -> list[str]:
    """Fetch, parse, and store one feed; returns buffered output lines."""
    global _logger
    lines: list[str] = []
    bump_processed, bump_added, bump_skipped, get_counts = pcounters()
    feedname = feed.name
    url = feed.url
    d = await asyncio.to_thread(feedparser.parse, url)
    if not silent:
        lines.append(f"+++\nFeed: {feedname}")
        lines.append(20 * "_")
        if d.bozo:
            lines.append("XML is ill-formed")
        lines.append(f"no. entries {len(d.entries)}")
    for entry in d.entries:
        bump_processed()
        dt = datetime.datetime(*entry.published_parsed[:6]) # pyright: ignore[reportArgumentType]
        entry["pubdate"] = dt
        ehash = hasher.ag_hash(entry.summary) # pyright: ignore[reportArgumentType]
        entry["hash"] = ehash
        already_in = await dbif.is_summary_in_db(ehash, entry.summary)
        if already_in:
            bump_skipped()
        else:
            entry.pop("summary_detail", "")
            entry.pop("title_detail", "")
            entry.pop("guidislink", "")
            entry.pop("media_credit", "")
            entry["pubname"] = pubname
            entry["feedname"] = feedname
            title = entry["title"]
            category = "uncategorized"
            if categorize:
                try:
                    category = await classify_by_title(title)
                except Exception as e:
                    msg = f"Classifier exception on title {title}: {e}"
                    if not silent:
                        lines.append(msg)
                    if not no_logging:
                        _logger.error(msg)
            entry["cat"] = category
            if no_store:
                lines.append(f"Would have stored title: {entry.title}")
            else:
                if not silent:
                    lines.append(f"saving *{entry['title']}* to category {entry['cat']}")
                await dbif.save_article(entry)
            bump_added()
    if not silent:
        lines.append(get_counts())
    return lines


async def parse_pub(
    pub: feeds.Publication,
    silent: bool,
    no_logging: bool,
    categorize: bool,
    no_store: bool = False,
):
    if not silent:
        print("\nPublication:", pub.name)
        print(20 * "*")
    feed_outputs = await asyncio.gather(*[
        process_feed(feed, pub.name, silent, no_logging, categorize, no_store)
        for feed in pub.feeds
    ])
    for feed_lines in feed_outputs:
        for line in feed_lines:
            print(line)
    if not silent:
        print(f"Done with pub {pub.name}\n")
        print(20 * "*")


async def process_pubs(
    xgroup: str | None,
    silent: bool,
    no_logging: bool,
    categorize: bool,
    no_store: bool = False,
):
    """Fetch all publications concurrently.

    Args:
        xgroup (str | None): if specified, exclude this group from the read
    """
    global _total_added, _total_processed, _total_skipped, _logger
    _total_added = _total_processed = _total_skipped = 0

    pubs = feeds.get_publications()
    if xgroup is not None:
        pubs = [pub for pub in pubs if pub.group != xgroup]

    async def safe_parse_pub(pub):
        try:
            await parse_pub(pub, silent, no_logging, categorize, no_store)
        except Exception as e:
            msg = f"Could not read {pub.name}: {e}"
            if not silent:
                print(msg)
            if not no_logging:
                _logger.error(msg)

    for pub in pubs:
        await safe_parse_pub(pub)

    ndocs = await dbif.get_article_count()
    msg = f"Tot: {_total_processed}, Added: {_total_added}, Skipped: {_total_skipped}. # of docs in db: {ndocs}"  # noqa
    if not silent:
        print(msg)
    if not no_logging:
        _logger.info(msg)


def main():
    pass


if __name__ == "__main__":
    main()
