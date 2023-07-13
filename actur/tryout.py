import actur.config.readconf as rc


def main():
    rc.read_conf()
    # print(pubs)
    pubs = rc.get_pubs()
    for pub in pubs:
        print("pubname:", pub["name"])
        feeds = pub["feeds"]
        for feed in feeds:
            # print(feed)
            print("  feedname:", feed[0])
            print("  url:", feed[1])


if __name__ == "__main__":
    main()
