import sentry_sdk

from actur.categorize import classify_by_title
from actur.utils.dbif import get_uncategorized_articles, update_article_cat


async def fix_uncategorized(dry_run: bool = False) -> tuple[int, int]:
    """Find articles with cat=='uncategorized' or missing cat, classify, and update.

    Returns (fixed, failed) counts.
    """
    fixed = 0
    failed = 0
    async for article in get_uncategorized_articles():
        article_id = article["_id"]
        title = article.get("title", "")
        try:
            category = await classify_by_title(title)
            if not category:
                print(f"Failed to classify {title!r}, defaulting to 'uncategorized'")
                category = "uncategorized"
            if dry_run:
                print(f"[dry-run] Would set: {title!r} -> {category}")
            else:
                await update_article_cat(article_id, category)
                print(f"Fixed: {title!r} -> {category}")
            fixed += 1
        except Exception as e:
            msg = f"Failed to classify {title!r}: {e}"
            sentry_sdk.capture_message(msg)
            print(msg)
            failed += 1
    return fixed, failed


