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
@click.option("--summary", is_flag=True, help="Display summaries")
@click.option("--list", is_flag=True, help="List publications")
@click.argument("pubnames", nargs=-1)
def main(
    list: bool,
    summary: bool,
    pubnames: list[str],
    start: str,
    end: str,
    days: int,
    hours: int,
):
    """Console script for actur."""
    if list:
        pubs = feeds.get_papers()
        print("Feeds:\n----\n")
        for pub in pubs:
            print(pub)
        return 0
    if (start or end) and (days or hours):
        print("Error: Cannot specify explicit start or end with days or hours option")
        return 0
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
        display.display_articles(articles, summary_flag=summary)

    return 0


if __name__ == "__main__":
    print(sys.path)
    sys.exit(main())  # pragma: no cover
