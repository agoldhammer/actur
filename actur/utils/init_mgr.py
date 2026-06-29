from actur.config import readconf as rc
from actur.utils import sentry_helper
from actur.utils.dbif import init_db


def init_all():
    rc.read_conf()
    init_db()
    sentry_helper.init_sentry()
    print("All initializations complete.")

    
