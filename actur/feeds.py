from dataclasses import dataclass
from typing import List


@dataclass
class Feed:
    name: str
    url: str


@dataclass
class Publication:
    name: str
    feeds: List[Feed]


lemonde = Publication(
    name="LeMonde",
    feeds=[
        Feed("Politique", "https://www.lemonde.fr/politique/rss_full.xml"),
        Feed("Une", "https://www.lemonde.fr/rss/une.xml"),
        Feed("Idées", "https://www.lemonde.fr/idees/rss_full.xml"),
    ],
)

liberation = Publication(
    name="Libération",
    feeds=[
        Feed(
            "all", "https://www.liberation.fr/arc/outboundfeeds/rss-all/?outputType=xml"
        )
    ],
)

sz = Publication(
    name="SZ", feeds=[Feed("TopThemen", "https://rss.sueddeutsche.de/rss/Topthemen")]
)

corriere = Publication(
    name="Corriere della Sera",
    feeds=[Feed("all", "http://xml2.corriereobjects.it/rss/homepage.xml")],
)

europapers = [lemonde, sz, corriere, liberation]


def get_papers() -> List[Publication]:
    return europapers
