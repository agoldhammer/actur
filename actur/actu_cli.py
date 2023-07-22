import sys
from time import sleep

import click

from actur.utils import display, feeds, query
from actur import reader


@click.group()
def cli():
    # click.echo("actu Newsreader")
    pass


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
            print(f"Name: {pub.name} - Group: {pub.group}")
            for feed in pub.feeds:
                print(f"...Feed name: {feed.name}")
            print(20 * "=")
        return 0
    # select articles
    articles = query.get_arts_in_daterange_from_pubs(
        pubnames, start, end, days, hours, group
    )
    display.display_articles(articles, summary_flag=summary)

    return 0


@cli.command()
@click.option("--xgroup", "-x", help="Group to exclude from read (opt)")
@click.option("--silent", is_flag=True, help="No console output")
@click.option("--no-logging", is_flag=True, help="Do not write to log file")
@click.option("--daemon", "-d", is_flag=True, help="Run as daemon")
@click.option("--sleeptime", type=int, default=1800, help="Time to sleep in secs")
def read(xgroup, silent: bool, no_logging: bool, daemon: bool, sleeptime: int):
    """Check news feeds for new articles"""
    try:
        reader.setup_logging()
        while True:
            reader.process_pubs(xgroup, silent, no_logging)
            if daemon:
                sleep(sleeptime)
            else:
                break
    except Exception as e:
        print(f"Could not read feeds: {e}")


if __name__ == "__main__":
    print(sys.path)
    sys.exit(cli())  # pragma: no cover
