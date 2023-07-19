from dataclasses import dataclass

from actur.config import readconf as rc

# from actur.utils import dbif


@dataclass
class Feed:
    name: str
    url: str


@dataclass
class Publication:
    name: str
    group: str
    feeds: list[Feed]


def make_feed(name_url_pair: list) -> Feed:
    return Feed(name_url_pair[0], name_url_pair[1])


def make_pub(name: str, group: str, rawfeeds: list):
    feeds = []
    for feed in rawfeeds:
        feeds.append(make_feed(feed))
    return Publication(name=name, group=group, feeds=feeds)


def get_publications() -> list[Publication]:
    pubs = []
    # _ = dbif.get_db()
    rawpubs = rc.get_conf_by_key("Publications")
    for rawpub in rawpubs:
        name = rawpub["name"]
        group = rawpub["group"]
        feeds = rawpub["feeds"]
        pubs.append(make_pub(name, group, feeds))
    return pubs
