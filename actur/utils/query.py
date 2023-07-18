from actur.utils import dbif
import pendulum
import datetime as dt


def calc_time_range(
    start: str | None, end: str | None, days: int | None, hours: int | None
) -> tuple[str | None, dt.datetime | None, dt.datetime | None]:
    print("creating temp dr")
    print("Time Params:", start, end, days, hours)
    errmsg = None
    start_dt = None
    end_dt = None
    if (start or end) and (days or hours):
        errmsg = "Cannot specify explicit start or end with days or hours option"
        return errmsg, None, None
    end_dt = pendulum.now().in_timezone("UTC")
    start_dt = end_dt
    if days is not None:
        start_dt = start_dt.subtract(days=days)
    if hours is not None:
        start_dt = start_dt.subtract(hours=hours)
    return None, start_dt, end_dt


def create_temp_daterange(
    start: str | None, end: str | None, days: int | None, hours: int | None
):
    errmsg, start_dt, end_dt = calc_time_range(start, end, days, hours)
    if errmsg is not None:
        print(f"Error: {errmsg}")
    else:
        # print("Range", start_dt, end_dt)
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
    # create_temp_daterange(start=None, end=None, days=1, hours=None)
    main()
