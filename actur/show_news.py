"""Console script for actur."""
import sys
import click
from actur.utils import query
from actur.utils import dbif


@click.command()
@click.option("--pubname", "-p", multiple=True, default=["all"])
@click.option("--start", "-s")
@click.option("--end", "-e")
@click.option("--days", "-d")
@click.option("--hours", "-h")
@click.option("--summ/--no-summ", default=True)
def main(pubname: str, start: str, end: str, summ: bool, days: str, hours: str):
    """Console script for actur."""
    dbif.init_db("mongodb://elite.local")
    if days is not None or hours is not None:
        print("creating temp dr")
        query.create_temp_daterange(days, hours)
    return 0


if __name__ == "__main__":
    print(sys.path)
    sys.exit(main())  # pragma: no cover
