import hashlib

import bs4


def normalize_summary(text: str) -> str:
    """Strip HTML markup and collapse whitespace so that cosmetic
    differences between fetches of the same article (re-tagged links,
    entity re-encoding, stray whitespace) don't defeat duplicate
    detection."""
    stripped = bs4.BeautifulSoup(text, "html.parser").get_text()
    return " ".join(stripped.split())


def ag_hash(text: str) -> str:
    digest = hashlib.sha256(text.encode(), usedforsecurity=False).hexdigest()
    return digest[:16]


def main():
    print(hashlib.algorithms_guaranteed)
    hashed = ag_hash("test")
    print(hashed)
    print(ag_hash("Now is the time for all good men"))


if __name__ == "__main__":
    main()
