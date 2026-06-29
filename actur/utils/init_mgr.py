from actur.config import readconf as rc
from actur.utils.dbif import init_db


def init_all():
    rc.read_conf()
    init_db()
    print("All initializations complete.")

    
