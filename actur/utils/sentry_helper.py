import sentry_sdk

from actur.config import readconf as rc

_sentry_initialized = False

def init_sentry():
    dsn = rc.get_conf_by_key("sentry")["dsn"]
    sample_rate = rc.get_conf_by_key("sentry")["sample_rate"]
    if dsn and sample_rate:
        sentry_sdk.init(
            dsn = dsn,
            traces_sample_rate = sample_rate,
            profiles_sample_rate = sample_rate
        )
        global _sentry_initialized
        _sentry_initialized = True
        print("Sentry initialized.")
    else:
        print("Sentry not initialized due to missing configuration.")
    
async def sentry_output(msg):
    if _sentry_initialized:
        sentry_sdk.capture_message(msg)
        await sentry_sdk.flush_async()
    else:
        print(f"Sentry not initialized, cannot capture message {msg}.")
