from dataclasses import dataclass

from actur.config import readconf as rc


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


# def set_pubs_from_conf():
#     rawpubs = readconf.read_conf()
#     for rawpub in rawpubs:
#         feeds = [make_feed(*feed) for feed in rawpub["feeds"]]
#         # pub = Publication(rawpub["name"], feeds)
#     return feeds


# lemonde = Publication(
#     name="LeMonde",
#     group="French",
#     feeds=[
#         Feed("Politique", "https://www.lemonde.fr/politique/rss_full.xml"),
#         Feed("Une", "https://www.lemonde.fr/rss/une.xml"),
#         Feed("Idées", "https://www.lemonde.fr/idees/rss_full.xml"),
#     ],
# )

# liberation = Publication(
#     name="Libération",
#     group="French",
#     feeds=[
#         Feed(
#             "all", "https://www.liberation.fr/arc/outboundfeeds/rss-all/?outputType=xml"
#         )
#     ],
# )

# sz = Publication(
#     name="SZ",
#     group="German",
#     feeds=[Feed("TopThemen", "https://rss.sueddeutsche.de/rss/Topthemen")],
# )

# corriere = Publication(
#     name="Corriere",
#     group="Italian",
#     feeds=[Feed("all", "http://xml2.corriereobjects.it/rss/homepage.xml")],
# )

# zeit = Publication(
#     name="Zeit",
#     group="German",
#     feeds=[Feed("Zeit - all", "https://newsfeed.zeit.de/index")],
# )

# handelsblatt = Publication(
#     name="Handelsblatt",
#     group="German",
#     feeds=[
#         Feed(
#             "Handelsblatt - all",
#             "https://www.handelsblatt.com/contentexport/feed/top-themen",
#         )
#     ],
# )

# faz = Publication(
#     name="FAZ", group="German", feeds=[Feed("FAZ - all", "https://faz.net/rss/aktuel")]
# )

# echos = Publication(
#     name="LesEchos",
#     group="French",
#     feeds=[
#         Feed("Echos - Idées", "https://services.lesechos.fr/rss/les-echos-idees.xml"),
#         Feed(
#             "Echos - Economie",
#             "https://services.lesechos.fr/rss/les-echos-economie.xml",
#         ),
#         Feed(
#             "Echos - Finance/Marchés",
#             "https://services.lesechos.fr/rss/les-echos-finance-marches.xml",
#         ),
#     ],
# )

# europapers = [lemonde, sz, corriere, liberation, zeit, handelsblatt, echos]


# def get_papers() -> list[Publication]:
#     return europapers


def get_publications() -> list[Publication]:
    pubs = []
    rawpubs = rc.get_conf_by_key("Publications")
    for rawpub in rawpubs:
        name = rawpub["name"]
        group = rawpub["group"]
        feeds = rawpub["feeds"]
        pubs.append(make_pub(name, group, feeds))
    return pubs
