import asyncio
import logging
import os
import sys
import time

import click

from actur import fix_uncategorized, reader
from actur.config import readconf as rc
from actur.utils import dbif, display, feeds, init_mgr, query


class GlobalLogger:
    _logger: logging.Logger | None = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        init_mgr.init_all()
        if cls._logger is None:
            cls._logger = setup_logging()
        return cls._logger


def setup_logging():
    LOGFILEPATH = rc.get_conf_by_key("logfilepath")["path"]
    if not os.access(LOGFILEPATH, os.W_OK):
        raise Exception(f"Logfile {LOGFILEPATH} does not exist or is not writable")
    _logger = logging.getLogger("actu-rdr-log")
    _logger.setLevel(logging.INFO)
    fh = logging.FileHandler(LOGFILEPATH)
    fh.setLevel(logging.INFO)
    myformat = logging.Formatter("%(asctime)s-%(name)s:%(levelname)s--%(message)s")
    logging.Formatter.converter = time.gmtime
    fh.setFormatter(myformat)
    _logger.addHandler(fh)
    return _logger


@click.version_option(
    None,
    "--version",
    "-v",
    package_name="actur",
    prog_name="actu",
)
@click.group()
def cli():
    # init_mgr.init_all()
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
    async def _fetch_and_display():
        articles = await query.get_arts_in_daterange_from_pubs(
            pubnames, start, end, days, hours, group
        )
        await display.display_articles(articles, summary_flag=summary)

    try:
        asyncio.run(_fetch_and_display())
    except Exception as e:
        print(f"Error showing articles: {e}")

    return 0


@cli.command()
@click.option("--xgroup", "-x", help="Group to exclude from read (opt)")
@click.option("--silent", is_flag=True, help="No console output")
@click.option("--no-logging", is_flag=True, help="Do not write to log file")
@click.option("--daemon", "-d", is_flag=True, help="Run as daemon")
@click.option("--sleeptime", type=int, default=1800, help="Time to sleep in secs")
@click.option("--categorize", is_flag=True, help="Categorize with ChatGPT")
@click.option(
    "--no-store", "-n", is_flag=True, help="Read feeds only, do not store in database."
)
def read(
    xgroup,
    silent: bool,
    no_logging: bool,
    daemon: bool,
    sleeptime: int,
    categorize: bool,
    no_store: bool,
    logger: logging.Logger = GlobalLogger.get_logger(),
):
    """Check news feeds for new articles"""
    try:

        async def run():
            await dbif.ensure_indexes()
            cycle = 0
            while True:
                await reader.process_pubs(
                    xgroup, silent, no_logging, categorize, no_store, logger
                )
                if daemon:
                    if not silent:
                        print(f"Sleeping for {sleeptime} seconds...")
                    if not no_logging:
                        cycle += 1
                        logger.info(
                            f"***Sleeping cycle {cycle} for {sleeptime} seconds..."
                        )
                    await asyncio.sleep(sleeptime)
                else:
                    if not silent:
                        print("Exiting...")
                    break

        asyncio.run(run())
    except Exception as e:
        print(f"Could not read feeds: {e}")


@cli.command("fix-uncategorized")
@click.option("--dry-run", is_flag=True, help="Preview without writing to database")
def fix_uncategorized_cmd(dry_run: bool):
    """Classify articles stored as 'uncategorized' or missing a category"""

    async def _run():
        fixed, failed = await fix_uncategorized.fix_uncategorized(dry_run=dry_run)
        label = "[dry-run] " if dry_run else ""
        print(f"{label}Done. Fixed: {fixed}, Failed: {failed}")

    try:
        asyncio.run(_run())
    except Exception as e:
        print(f"Error fixing uncategorized articles: {e}")


def main():
    cli()


if __name__ == "__main__":
    main()
    sys.exit(0)
