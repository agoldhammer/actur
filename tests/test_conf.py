from actur.config import readconf
from actur.utils import dbif

# import pytest


# @pytest.fixture()
# def setup():
#     dbif.init_db()


def test_conf_by_key():
    dbif.init_db()
    res = readconf.get_conf_by_key("database")
    assert "dbname" in res  # nosec
