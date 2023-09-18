# Notes for ACTUR project

<!-- markdownlint-disable MD030 -->

## TODO

-   signal handler?
-   run with supervisord
-   redo getconf
-   graphql

## coverage

pytest --cov=actur tests/

## on git guardian and precommit hooks

[https://docs.gitguardian.com/ggshield-docs/integrations/git-hooks/pre-commit#:~:text=A%20pre%2Dcommit%20hook%20is,through%20our%20CLI%20application%3A%20ggshield%20.]

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
# install config files atlas.toml, local.toml
sudo mkdir -p /var/log/actu
sudo touch /var/log/actu/reader-local.log
sudo chown -R $(whoami) /var/log/actu/reader-local.log
actu read -x US
sudo touch /var/log/actu/reader-atlas.log
sudo chown -R $(whoami) /var/log/actu/reader-atlas.log

```

Copy sup-actur.conf to /etc/supervisor/conf.d actur.conf
and restart supervisor supervisorctl start actur-atlas actur-local
omit atlas if no longer being used
