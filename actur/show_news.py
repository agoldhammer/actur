"""Console script for actur."""
import sys

import click

from actur.utils import dbif, display, feeds, query


@click.command()
@click.option("--pubname", "-p", multiple=True, default=["all"], help="pubname")
@click.option("--start", "-s", help="start date")
@click.option("--end", "-e", help="end date")
@click.option("--days", "-d", type=int, help="days ago")
@click.option("--hours", "-h", type=int, help="hours ago")
@click.option("--summ/--no-summ", default=True)
def main(pubname: list[str], start: str, end: str, summ: bool, days: int, hours: int):
    """Console script for actur."""
    dbif.init_db("mongodb://elite.local")
    if days is not None or hours is not None:
        print("creating temp dr")
        print(days, hours)
        query.create_temp_daterange(days, hours)
        db = dbif.get_db()
        # pubname is a list, since it may be specified multiple times
        # on command line
        if "all" in pubname:
            pubname = [pub.name for pub in feeds.get_papers()]
        articles = db.daterange.find({"pubname": {"$in": pubname}}).sort("pubdate", 1)
        display.display_articles(articles)

    return 0


if __name__ == "__main__":
    print(sys.path)
    sys.exit(main())  # pragma: no cover
