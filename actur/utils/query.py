import datetime as dt
import sys

import pendulum as pd
import pendulum.parsing as pa

from actur.utils import dbif, feeds

DT = dt.datetime


def daterange_from_deltas(
    days: int | None, hours: int | None
) -> tuple[str | None, DT | None, DT | None]:
    end_dt = pd.now().in_timezone("UTC")
    start_dt = end_dt
    if days is not None:
        start_dt = start_dt.subtract(days=days)
    if hours is not None:
        start_dt = start_dt.subtract(hours=hours)
    return None, start_dt, end_dt


def calc_time_range(
    start: str | None, end: str | None, days: int | None, hours: int | None
) -> tuple[str | None, DT | None, DT | None]:
    print("Creating temporary daterange collection")
    #print("Time Params:", start, end, days, hours)
    errmsg = None
    start_dt = None
    end_dt = None
    if (start or end) and (days or hours):
        errmsg = "Cannot specify explicit start or end with days or hours option"
        return errmsg, None, None
    if days or hours:
        return daterange_from_deltas(days, hours)
    if end and start is not None:
        start_dt = pa.parse(start)
    else:  # assume 1 day ago for missing start
        start_dt = pd.now().in_timezone("UTC").subtract(days=1)
    if end is None:
        end_dt = pd.now().in_timezone("UTC")
    else:
        end_dt = pa.parse(end)
    return None, start_dt, end_dt # type: ignore


async def create_temp_daterange(
    start: str | None, end: str | None, days: int | None, hours: int | None
):
    errmsg = None
    try:
        errmsg, start_dt, end_dt = calc_time_range(start, end, days, hours)
    except pa.exceptions.ParserError as exc: # type: ignore
        print(f"Error parsing date: {exc}\n")
        sys.exit(255)
    if errmsg is not None:
        print(f"Error: {errmsg}\n")
    else:
        print(f"New date range: {start_dt} to {end_dt}\n")
        await dbif.make_tempdb_from_daterange(start_dt, end_dt)


async def get_arts_in_daterange_from_pubs(
    pubnames: list[str],
    start: str | None,
    end: str | None,
    days: int | None,
    hours: int | None,
    group: str | None = None,
):
    await create_temp_daterange(start, end, days, hours)

    if "all" in pubnames:
        pubnames = [pub.name for pub in feeds.get_publications()]
    if group is not None:
        pubnames = [pub.name for pub in feeds.get_publications() if pub.group == group]
    return dbif.get_articles_in_daterange(pubnames)

