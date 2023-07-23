from actur.utils import dbif
from collections import defaultdict

"""Detect duplicate articles in articles collection of db actur"""

_hashdict = defaultdict(list)


def main():
    dupes = []
    arts = dbif.find_all()
    for art in arts:
        _hashdict[art["hash"]].append(art["_id"])
    [dupes.append(idlist) for _, idlist in _hashdict.items() if len(idlist) > 1]
    # for _, idlist in _hashdict.items():
    #     print(len(idlist))
    print(dupes)


if __name__ == "__main__":
    main()
