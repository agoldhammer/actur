"""Console script for actur."""
import sys

import click

from actur.utils import dbif, display, feeds, query


@click.command()
# @click.option("--pubname", "-p", multiple=True, default=["all"], help="pubname")
@click.option("--start", "-s", help="start date")
@click.option("--end", "-e", help="end date")
@click.option("--days", "-d", type=int, help="days ago")
@click.option("--hours", "-h", type=int, help="hours ago")
@click.option("--summ/--no-summ", default=True)
@click.argument("pubnames", nargs=-1)
def main(pubnames: list[str], start: str, end: str, summ: bool, days: int, hours: int):
    """Console script for actur."""
    dbif.init_db()
    if days is not None or hours is not None:
        print("creating temp dr")
        print(days, hours)
        query.create_temp_daterange(days, hours)
        # pubname is a list, since it may be specified multiple times
        # on command line
        if "all" in pubnames:
            pubnames = [pub.name for pub in feeds.get_papers()]
        articles = dbif.get_articles_in_daterange(pubnames)
        display.display_articles(articles)

    return 0


if __name__ == "__main__":
    print(sys.path)
    sys.exit(main())  # pragma: no cover
