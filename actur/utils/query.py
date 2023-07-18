import datetime as dt
import sys

import pendulum as pd
import pendulum.parsing as pa

from actur.utils import dbif

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
    # print("Time Params:", start, end, days, hours)
    errmsg = None
    start_dt = None
    end_dt = None
    if (start or end) and (days or hours):
        errmsg = "Cannot specify explicit start or end with days or hours option"
        return errmsg, None, None
    if days or hours:
        return daterange_from_deltas(days, hours)
    if end and not start:
        errmsg = "End specified without start"
        return errmsg, None, None
    else:
        if start is not None:
            start_dt = pa.parse(start)
        else:
            start_dt = pd.now().in_timezone("UTC").subtract(days=1)
    if end is None:
        end_dt = pd.now().in_timezone("UTC")
    else:
        end_dt = pa.parse(end)
    return None, start_dt, end_dt


def create_temp_daterange(
    start: str | None, end: str | None, days: int | None, hours: int | None
):
    errmsg = None
    try:
        errmsg, start_dt, end_dt = calc_time_range(start, end, days, hours)
    except pa.exceptions.ParserError as exc:
        print(f"Error parsing date: {exc}\n")
        sys.exit(255)
    if errmsg is not None:
        print(f"Error: {errmsg}\n")
    else:
        # print("Range", start_dt, end_dt)
        # print(f"Types: {type(start_dt)}, {type(end_dt)}\n")
        print(f"New date range: {start_dt} to {end_dt}\n")
        dbif.make_tempdb_from_daterange(start_dt, end_dt)


def main():
    pass


if __name__ == "__main__":
    dbif.init_db()
    # should return an error
    create_temp_daterange(start="2023-07-16", end=None, days=1, hours=1)
    create_temp_daterange("2023-07-16", "2023-07-17", None, None)
    create_temp_daterange(None, None, days=1, hours=None)
    create_temp_daterange(None, None, days=None, hours=1)
    create_temp_daterange(None, "2027-07-17", None, None)
    create_temp_daterange(start="2023-07-16T00:00", end=None, days=None, hours=None)
    # create_temp_daterange(start=None, end=None, days=1, hours=None)
    main()
