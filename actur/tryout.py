def main():
    from actur.utils import query, dbif

    articles = query.get_arts_in_daterange_from_pubs(["FT"], None, None, 0, 4, None)
    jquery = dbif.cursor_to_json(articles)
    print(jquery)


if __name__ == "__main__":
    main()
