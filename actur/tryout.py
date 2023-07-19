# import actur.config.readconf as rc
# import actur.utils.feeds as feeds


# def main():
#     rc.read_conf()
#     # print(pubs)
#     host = rc.get_conf_by_key("database")
#     pubs = rc.get_conf_by_key("Publications")
#     print("Host:", host)
#     for pub in pubs:
#         print("pubname:", pub["name"])
#         print("group:", pub["group"])
#         feeds = pub["feeds"]
#         for feed in feeds:
#             # print(feed)
#             print("  feedname:", feed[0])
#             print("  url:", feed[1])


# def main():
#     rc.read_conf()
#     conf_feeds = feeds.get_publications()
#     for feed in conf_feeds:
#         print(feed)
def main():
    # dbif.init_db()
    # db = dbif.get_db()
    # articles = dbif.find_text("daterange", "Macron Borne Mélenchon")
    # for article in articles:
    #     print(article["pubdate"])
    #     print(article["title"])
    #     print("...")
    from actur.utils import query, dbif

    articles = query.get_arts_in_daterange_from_pubs(["SZ"], None, None, 0, 4, None)
    jquery = dbif.cursor_to_json(articles)
    print(jquery)


if __name__ == "__main__":
    main()
