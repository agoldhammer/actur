import sentry_sdk
from config import readconf as rc

dsn = rc.get_conf_by_key("sentry")["dsn"]

sentry_sdk.init(
    dsn=rc.get_conf_by_key("sentry")["dsn"],
)

div_by_zero = 1 / 0
