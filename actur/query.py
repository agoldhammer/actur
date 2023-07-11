from actur import dbif
import pendulum


def create_temp_daterange(days: str | None, hours: str | None):
    now = pendulum.now().in_timezone("UTC")
    past = now
    if days is not None:
        past = past.subtract(days=int(days))
    if hours is not None:
        past = past.subtract(hours=int(hours))
    print("start, end:", past, now)
    dbif.make_tempdb_from_daterange(past, now)
    db = dbif.get_db()
    for art in db.daterange.find({}, {"pubdate": 1}):
        print(art)


def main():
    pass
    # dt = pendulum.parse("2023-07-08")
    # print(dt)
    # dt = pendulum.parse("July 7, 2023", strict=False)
    # print(dt)
    # dt = pendulum.parse("8 July 2022", strict=False)
    # print(dt)


if __name__ == "__main__":
    dbif.init_db("mongodb://elite.local")
    create_temp_daterange(days="1", hours=None)
    main()
