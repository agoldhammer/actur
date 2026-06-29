import sentry_sdk

from actur.config import readconf as rc


def init_sentry():
    sentry_sdk.init(
        dsn = rc.get_conf_by_key("sentry")["dsn"],
        traces_sample_rate = rc.get_conf_by_key("sentry")["sample_rate"],
        profiles_sample_rate = rc.get_conf_by_key("sentry")["sample_rate"],
    )
    
def sentry_output(msg):
    sentry_sdk.capture_message(msg)
