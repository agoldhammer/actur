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
    name="Corriere",
    feeds=[Feed("all", "http://xml2.corriereobjects.it/rss/homepage.xml")],
)

zeit = Publication(
    name="Zeit", feeds=[Feed("Zeit - all", "https://newsfeed.zeit.de/index")]
)

handelsblatt = Publication(
    name="Handelsblatt",
    feeds=[
        Feed(
            "Handelsblatt - all",
            "https://www.handelsblatt.com/contentexport/feed/top-themen",
        )
    ],
)

faz = Publication(name="FAZ", feeds=[Feed("FAZ - all", "https://faz.net/rss/aktuel")])

echos = Publication(
    name="LesEchos",
    feeds=[
        Feed("Echos - Idées", "https://services.lesechos.fr/rss/les-echos-idees.xml"),
        Feed(
            "Echos - Economie",
            "https://services.lesechos.fr/rss/les-echos-economie.xml",
        ),
        Feed(
            "Echos - Finance/Marchés",
            "https://services.lesechos.fr/rss/les-echos-finance-marches.xml",
        ),
    ],
)
"""
https://newsfeed.zeit.de/index
https://faz.net/rss/aktuel FEED has no attribute title, so excluding
https://www.handelsblatt.com/contentexport/feed/top-themen
https://services.lesechos.fr/rss/les-echos-idees.xml
https://services.lesechos.fr/rss/les-echos-economie.xml
https://services.lesechos.fr/rss/les-echos-finance-marches.xml

"""

europapers = [lemonde, sz, corriere, liberation, zeit, handelsblatt, echos]


def get_papers() -> List[Publication]:
    return europapers
