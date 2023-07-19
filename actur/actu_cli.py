import sys

import click

from actur.utils import display, feeds, query
from actur import reader


@click.group()
def cli():
    click.echo("CLI for actu newsreader")


@cli.command()
@click.option("--start", "-s", help="start date")
@click.option("--end", "-e", help="end date")
@click.option("--days", "-d", type=int, help="days ago")
@click.option("--hours", "-h", type=int, help="hours ago")
@click.option("--summary", is_flag=True, help="Display summaries")
@click.option("--list", is_flag=True, help="List publications")
@click.option("--group", "-g", help="group to show")
@click.argument("pubnames", nargs=-1)
def show(
    list: bool,
    summary: bool,
    pubnames: list[str],
    start: str,
    end: str,
    days: int,
    hours: int,
    group: str,
):
    """Select and display articles"""
    # list publications
    if list:
        pubs = feeds.get_publications()
        print("Feeds:\n----\n")
        for pub in pubs:
            print(pub)
        return 0
    # select articles
    articles = query.get_arts_in_daterange_from_pubs(
        pubnames, start, end, days, hours, group
    )
    display.display_articles(articles, summary_flag=summary)

    return 0


@cli.command()
@click.option("--xgroup", "-x", help="group to exclude from read (opt)")
def read(xgroup):
    """Check news feeds for new articles"""
    reader.process_pubs(xgroup)


if __name__ == "__main__":
    print(sys.path)
    sys.exit(cli())  # pragma: no cover
