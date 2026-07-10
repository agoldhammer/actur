import asyncio
from collections import defaultdict

import pendulum

from actur.config import readconf as rc
from actur.utils import dbif, hasher


async def main():
    rc.read_conf()
    dbif.init_db()
    db = dbif.get_db()

    end = pendulum.now().in_timezone("UTC")
    start = end.subtract(hours=24)

    cursor = db.articles.find(
        {"pubdate": {"$gte": start, "$lte": end}},
        {"pubdate": 1, "pubname": 1, "title": 1, "summary": 1, "hash": 1, "link": 1},
    )

    by_hash = defaultdict(list)
    count = 0
    async for art in cursor:
        count += 1
        by_hash[art.get("hash")].append(art)

    print(f"Total articles in last 24h: {count}")

    hash_dupes = {h: arts for h, arts in by_hash.items() if len(arts) > 1}
    print(f"Hash groups with >1 article: {len(hash_dupes)}")

    real_dupes = []
    for h, arts in hash_dupes.items():
        by_norm_summary = defaultdict(list)
        for a in arts:
            norm = hasher.normalize_summary(a.get("summary", ""))
            by_norm_summary[norm].append(a)
        for norm, group in by_norm_summary.items():
            if len(group) > 1:
                real_dupes.append(group)

    print(f"Confirmed duplicate groups (same hash + same normalized summary): {len(real_dupes)}")
    for group in real_dupes:
        print("---")
        for a in group:
            print(f"  id={a['_id']} pub={a.get('pubname')} pubdate={a.get('pubdate')} title={a.get('title')!r} link={a.get('link')}")

    # also flag same-hash-but-different-summary, just in case (hash collisions or near-dupes)
    non_confirmed = 0
    for h, arts in hash_dupes.items():
        norms = set(hasher.normalize_summary(a.get("summary", "")) for a in arts)
        if len(norms) > 1:
            non_confirmed += 1
    print(f"Hash groups with >1 article but differing normalized summaries: {non_confirmed}")


if __name__ == "__main__":
    asyncio.run(main())
