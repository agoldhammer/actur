# from click.testing import CliRunner
from actur.utils import query
import pendulum as pe


def test_from_deltas():
    errmsg, start_dt, end_dt = query.daterange_from_deltas(days=1, hours=None)
    assert errmsg is None  # nosec
    assert start_dt is not None  # nosec
    today = pe.now().in_timezone("UTC")
    if start_dt is not None:
        assert start_dt.hour == today.hour  # nosec
    assert end_dt is not None  # nosec
    assert end_dt.day == today.day  # nosec


def test_calc_time_range():
    res = query.calc_time_range(start="2023-07-18", end=None, days=1, hours=None)
    assert res[0] is not None  # nosec
    if res[0] is not None:
        assert "Cannot specify" in res[0]  # nosec

    res = query.calc_time_range(
        start="2023-07-17", end="2023-07-18", days=None, hours=None
    )
    assert res[0] is None  # nosec
    if res[1] is not None:
        assert res[1].day == 17  # nosec
    if res[2] is not None:
        assert res[2].day == 18  # nosec
