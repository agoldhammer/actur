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
        Feed("Une", "https://www.lemonde.fr/politique/rss_full.xml"),
        Feed("Politique", "https://www.lemonde.fr/politique/rss_full.xml"),
    ],
)

sz = Publication(
    name="SZ", feeds=[Feed("TopThemen", "https://rss.sueddeutsche.de/rss/Topthemen")]
)

corriere = Publication(
    name="Corriere della Sera",
    feeds=[Feed("all", "http://xml2.corriereobjects.it/rss/homepage.xml")],
)

europapers = [lemonde, sz, corriere]


def get_papers() -> List[Publication]:
    return europapers
