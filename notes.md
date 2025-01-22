# Notes for ACTUR project

<!-- markdownlint-disable MD030 -->

## TODO

-   signal handler?
-   run with supervisord
-   redo getconf
-   graphql

## coverage

pytest --cov=actur tests/

## proposed signal handler

```python
import signal

class GracefulInterruptHandler(object):

    def __init__(self, sig=signal.SIGINT):
        self.sig = sig

    def __enter__(self):

        self.interrupted = False
        self.released = False

        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)

        return self

    def __exit__(self, type, value, tb):
        self.release()

    def release(self):

        if self.released:
            return False

        signal.signal(self.sig, self.original_handler)

        self.released = True

        return True
```

See:
[https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python]

## Setup new machine

```bash
mkdir -p ~/.actu
# install config files local.toml
sudo mkdir -p /var/log/actu
sudo touch /var/log/actu/reader-local.log
sudo chown -R $(whoami) /var/log/actu/reader-local.log
actu read -x US
sudo touch /var/log/actu/reader-local.log
sudo chown -R $(whoami) /var/log/actu/reader-local.log

For display to work, must export ACTUCONF=$HOME/.actur/local.toml (this is now the default, so no need to specify explicitly)

```

Copy sup-actur.conf to /etc/supervisor/conf.d/actur.conf

and restart supervisor supervisorctl start actur-local [or start all if actuproxy being used]

New openai interface:

discussion [https://github.com/openai/openai-python/discussions/742]

## commands

actu read --categorize [--silent] [-d]

actu show -h 3 all
