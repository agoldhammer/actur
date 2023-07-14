import actur.config.readconf as rc


def main():
    rc.read_conf()
    # print(pubs)
    host = rc.get_conf_by_key("database")
    pubs = rc.get_conf_by_key("Publications")
    print("Host:", host)
    for pub in pubs:
        print("pubname:", pub["name"])
        print("group:", pub["group"])
        feeds = pub["feeds"]
        for feed in feeds:
            # print(feed)
            print("  feedname:", feed[0])
            print("  url:", feed[1])


if __name__ == "__main__":
    main()
