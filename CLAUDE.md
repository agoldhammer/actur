# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`actur` is a personal RSS news reader/aggregator. It polls configured RSS feeds, dedupes and stores articles in MongoDB, optionally classifies each article's topic via the OpenAI API, and provides a CLI (`actu`) to fetch and display articles. Requires Python >=3.11 (uses `tomllib` and `X | None` union syntax).

## Required runtime environment

Almost nothing in this package works without external state set up first — config files and a live MongoDB instance are read **at import time** (see Architecture below), not lazily, so even importing `actur.utils.dbif` or running most tests will fail without them.

- **Config file**: a TOML file, default path `~/.actur/local.toml`, overridable via the `ACTURCONF` env var (note: `notes.md` refers to an older `ACTUCONF` var name — the code's actual env var is `ACTURCONF`).
  - Top-level keys expected: `logfilepath.path`, `database.url` / `database.dbname`, `feedconfig.path` (path to a second TOML file).
  - The second TOML file (pointed to by `feedconfig.path`) defines `Publications` — a list of `{name, group, feeds: [[feedname, url], ...]}`.
  - `openai.secret_key` is read from the same merged config when `--categorize` is used.
- **MongoDB**: must be reachable at `database.url`; `actur.utils.dbif` connects and creates indexes on import.
- Deployment in practice runs two daemonized instances via supervisord (`sup-actur.conf`), each with its own `ACTURCONF` profile (e.g. `atlas.toml`, `local.toml`); only the `local` instance has `--categorize` enabled.

## Common commands

```bash
make lint          # flake8 + black --check over actur/ and tests/
make test          # pytest (default Python)
make test-all       # tox across py36/py37/py38 envs (see note on Python versions below)
make coverage       # coverage run --source actur -m pytest, then HTML report
pytest tests/test_query.py::test_calc_time_range   # run a single test
make docs           # sphinx-apidoc + build HTML docs
make dist           # build sdist/wheel
```

Most of `tests/` (`test_dbif.py`, `test_conf.py`, `test_query.py`) are **integration tests** that hit a real MongoDB and a real `ACTURCONF` config with live `Publications` (e.g. assertions check for specific publication names like `"LeMonde"`, `"SZ"`, `"FT"`). `tests/test_conf.py::test_feeds` additionally makes live network calls to every configured feed URL and is tagged `@pytest.mark.no_cover` to mark it as slow/excludable. There is no mocking layer — these tests are not safe to run without the same environment described above.

## Architecture

- **Config loading (`actur/config/readconf.py`)**: module-level singleton. `_read_conf()` runs once on import, reads the main TOML pointed to by `ACTURCONF`, then merges in the feed-config TOML it references via `feedconfig.path`. All other modules read config through `get_conf_by_key(key)`.
- **DB layer (`actur/utils/dbif.py`)**: module-level singleton pymongo client, also initialized on import (`_init_db()` at bottom of file calls `rc.get_conf_by_key`). All article reads/writes go through this module. Two key patterns to know:
  - Dedup: articles are matched by a truncated SHA-256 hash of the summary text (`hasher.ag_hash`), then confirmed by exact summary string match (`is_summary_in_db`) before insert.
  - Date-bounded queries work via a **temp collection**: `query.get_arts_in_daterange_from_pubs` first calls `dbif.make_tempdb_from_daterange`, which runs a `$match`+`$out` aggregation into a `daterange` collection, which is then queried/sorted by `dbif.get_articles_in_daterange`. This means every "show" query rebuilds the `daterange` collection from scratch first.
- **Feed model (`actur/utils/feeds.py`)**: `Feed`/`Publication` dataclasses are built fresh from config on each call to `get_publications()` — not cached.
- **Fetch pipeline (`actur/reader.py`)**: `process_pubs` → `parse_pub` → `process_feed`, one feed at a time via `feedparser`. Per entry: compute pubdate/hash, skip if already in DB, otherwise strip noisy fields (`summary_detail`, `title_detail`, `guidislink`, `media_credit`), optionally classify via `categorize.classify_by_title`, then `dbif.save_article`. Counters (processed/added/skipped) are tracked through closures returned by `pcounters()`, both per-feed and as running globals across the whole run. Logging is file-based via the module-level `_logger`, set up once by `setup_logging()` (called from the CLI before the read loop).
- **Categorization (`actur/categorize.py`)**: `classify_by_title` sends just the article title to OpenAI (`gpt-4o-mini`) with a fixed, hardcoded list of topic categories in the prompt; the reply is used verbatim as the article's `cat` field. There's no validation that the reply is actually one of the listed categories.
- **CLI (`actur/actu_cli.py`)**: Click group with two commands:
  - `actu show [pubnames...] [--list] [--summary] [--start/--end | --days/--hours] [--group]` — list publications, or query+display articles in a date range (delegates to `query.get_arts_in_daterange_from_pubs` + `display.display_articles`).
  - `actu read [--xgroup] [--silent] [--no-logging] [--daemon/-d] [--sleeptime] [--categorize]` — runs `reader.process_pubs` once or in a sleep loop.
- **Display (`actur/utils/display.py` + `summary_parser.py`)**: console output is colorized with `colorama`; article summaries are HTML, parsed with BeautifulSoup (`summary_parser.summary_parse`) to extract plain text plus an optional image `src`.
- **Standalone debug scripts**: `actur/tryout.py` and `actur/tryfeed.py` are ad hoc scripts (not part of the CLI) for testing the OpenAI classifier and a single feed URL respectively — run directly with `python -m`, not through `actu`.

## Things to watch for

- Packaging migrated from pip (`setup.py`/`setup.cfg`/`requirements*.txt`) to `uv`/`pyproject.toml`. Runtime deps (`click`, `pymongo`, `feedparser`, `openai`, `pendulum`, `beautifulsoup4`, `colorama`) live in `[project.dependencies]`; dev tools (`pytest`, `black`, `sphinx`, `twine`, `tox`, etc.) live in `[dependency-groups] dev`. Use `uv sync`, `uv run <tool>`, `uv lock`, `uv build`. A `.python-version` pins 3.11 since this sandbox's system Python (3.14) lacks a C compiler for source-only builds of packages like `time-machine`.
- The `readnews` console-script entry point (`actur.reader:main`) is currently a no-op stub (`main()` is just `pass`) — actual feed-reading is invoked through `actu read`, not `readnews`.
- `tox.ini`/`.travis.yml` target Python 3.6–3.8, but `pyproject.toml` declares `requires-python = ">=3.11"` and the code uses 3.11+ syntax (`tomllib`, PEP 604 unions) — the tox/travis configs are stale relative to the actual language version in use.
- `.pre-commit-config.yaml` has its only hook (ggshield) fully commented out, so no pre-commit hooks currently run.
