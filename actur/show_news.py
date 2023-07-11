"""Console script for actur."""
import sys
import click
from actur.utils import dbif, display, query


@click.command()
@click.option("--pubname", "-p", multiple=True, default=["all"], help="pubname")
@click.option("--start", "-s", help="start date")
@click.option("--end", "-e", help="endate")
@click.option("--days", "-d", type=int, help="days ago")
@click.option("--hours", "-h", type=int, help="hours ago")
@click.option("--summ/--no-summ", default=True)
def main(pubname: str, start: str, end: str, summ: bool, days: int, hours: int):
    """Console script for actur."""
    dbif.init_db("mongodb://elite.local")
    if days is not None or hours is not None:
        print("creating temp dr")
        print(days, hours)
        query.create_temp_daterange(days, hours)
        db = dbif.get_db()
        if pubname is not None:
            articles = db.daterange.find({"pubname": pubname[0]})
            for article in articles:
                display.display_article(article)

    return 0


if __name__ == "__main__":
    print(sys.path)
    sys.exit(main())  # pragma: no cover
