# import asyncio

# from actur.utils import dbif, query


# async def main():
#     await dbif.init_db()
#     articles = await query.get_arts_in_daterange_from_pubs(["FT"], None, None, 0, 4, None)
#     jquery = dbif.cursor_to_json(await articles.to_list(None))
#     print(jquery)


# if __name__ == "__main__":
#     asyncio.run(main())
