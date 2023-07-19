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
    if list:
        pubs = feeds.get_publications()
        print("Feeds:\n----\n")
        for pub in pubs:
            print(pub)
        return 0
    # creating temporary data range

    # query.create_temp_daterange(start, end, days, hours)
    articles = query.get_pubs_in_daterange(pubnames, start, end, days, hours, group)
    # pubname is a list, since it may be specified multiple times
    # on command line
    # if "all" in pubnames:
    #     pubnames = [pub.name for pub in feeds.get_publications()]
    # if group is not None:
    #     pubnames = [pub.name for pub in feeds.get_publications() if pub.group == group]
    # articles = dbif.get_articles_in_daterange(pubnames)
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
