# Code Review — `async` branch (2026-06-28)

## Findings

### 1. Critical — `dbif.py:35` — `init_db()` hard-requires `[sentry]` config, breaking all existing deployments

`init_db()` unconditionally calls `rc.get_conf_by_key("sentry")` inside the same `try` block as DB initialization. Any deployment without a `[sentry]` section in its TOML gets an `ActuDBError("Error initializing database: ...")` at startup — a misleading message that hides the true cause. Both `actu read` and `actu show` fail immediately.

**Fix:** Make Sentry init optional; only call `sentry_sdk.init()` when the `sentry` key is present in config.

---

### Fixed 2. High — `reader.py:88` — `entry.published_parsed` can be `None`, crashing entire feed

```python
dt = datetime.datetime(*entry.published_parsed[:6])
```

Feedparser sets `published_parsed = None` when it cannot parse the publication date. `None[:6]` raises `TypeError`, propagating up through `process_feed` and killing all remaining entries in the feed.

**Fix:** Guard with `if entry.published_parsed is None: bump_skipped(); continue` before this line.

---

### 3. High — `reader.py:90` — Missing `summary` field raises `AttributeError`, drops remaining entries

```python
ehash = hasher.ag_hash(entry.summary)
```

RSS 2.0 entries may legally omit `<description>`/`<summary>`. Feedparser's `FeedParserDict.__getattr__` re-raises the missing key as `AttributeError`, which propagates out of the `for entry` loop and silently drops all subsequent entries in the feed.

**Fix:** Use `entry.get("summary")` and skip or handle the `None` case.

---

### 4. High — `query.py:37` — `--start` silently discarded when no `--end` is given

```python
if end and start is not None:
    start_dt = pa.parse(start)
else:  # assume 1 day ago for missing start
    start_dt = pd.now().in_timezone("UTC").subtract(days=1)
```

When `end` is `None` (falsy), `None and True` short-circuits to `False` regardless of `start`. The `else` branch overwrites `start_dt` with "now − 1 day", silently discarding the user's explicit `--start` value. No error is shown.

**Fix:** Change condition to `if start is not None:` (parse start independently of end), and handle the `end`-only case separately.

---

### 5. Medium — `reader.py:92` — `--no-store` dry-run still requires a live MongoDB connection

```python
already_in = await dbif.is_summary_in_db(ehash, entry.summary)  # line 92
...
if no_store:
    lines.append(f"Would have stored title: ...")
else:
    await dbif.save_article(entry)
```

The dedup check at line 92 hits MongoDB for every entry regardless of `no_store`. Additionally, `process_pubs` calls `await dbif.get_article_count()` unconditionally at line 182. A user attempting a dry-run without a live DB gets a connection error, not a graceful preview.

**Fix:** Short-circuit the dedup and count calls when `no_store=True`, or document that a DB connection is always required.

---

### 6. Medium — `display.py:31` — `article['link']` raises `KeyError` for articles stored without a link

```python
print(f"\n{Fore.LIGHTMAGENTA_EX}{article['link']}{Style.RESET_ALL}\n")
```

Some RSS/Atom entries have no `<link>` element. When such an article is stored and later displayed, the hard key lookup raises `KeyError`, halting display of all remaining articles in the query result.

**Fix:** Use `article.get('link', '')` and conditionally print the link line.

---

### 7. Low — `reader.py:121` — `bump_added()` outside `if no_store` block inflates counter in dry-run mode

```python
if no_store:
    lines.append(f"Would have stored title: ...")
else:
    ...
    await dbif.save_article(entry)
bump_added()  # runs unconditionally
```

In `--no-store` mode, `bump_added()` increments both the per-feed counter and `_total_added`, so the final summary reports `Added: N` when zero documents were written.

**Fix:** Move `bump_added()` inside the `else` branch (or add a separate `bump_would_have_added()` counter for no-store mode).

---

### 8. Low — `.python-version:1` — File contains `3.14` instead of `3.11`

CLAUDE.md states: "`.python-version` pins 3.11 since this sandbox's system Python (3.14) lacks a C compiler for source-only builds of packages like `time-machine`." The file currently contains `3.14`, causing `uv sync` to resolve to Python 3.14 and fail on source-only package builds.

**Fix:** Set `.python-version` back to `3.11`.

---

### 9. Low — `categorize.py:11` — `AsyncOpenAI` client created per article, connection pool never reused

```python
async def classify_by_title(title):
    client = AsyncOpenAI(api_key=get_conf_by_key("openai")["secret_key"])
```

`AsyncOpenAI` wraps an `httpx.AsyncClient` with its own connection pool. Creating one per call means no connection reuse, and the client is never explicitly closed (no `async with`), so connections and file descriptors accumulate until GC runs. In daemon mode with many articles per run, this is a resource leak.

**Fix:** Create the client once at module level (initialized after config is loaded, following the `init_db` pattern), or pass it as a parameter.

---

### 10. Low — `reader.py:179` — Publications processed sequentially, contradicting "concurrently" docstring

```python
for pub in pubs:
    await safe_parse_pub(pub)
```

The docstring at line 156 says "Fetch all publications concurrently," but pubs are processed one at a time. The per-pub `asyncio.gather` for feeds (line 137) shows the pattern is understood; the fix is straightforward since `safe_parse_pub` already catches per-pub exceptions.

**Fix:** Replace the loop with `await asyncio.gather(*[safe_parse_pub(pub) for pub in pubs])`. Note: `parse_pub` currently `print()`s the publication header directly (line 135); that line should be moved into the buffered `lines` list before enabling true pub-level concurrency to avoid interleaved output.
