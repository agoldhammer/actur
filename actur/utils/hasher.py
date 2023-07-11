import hashlib


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
