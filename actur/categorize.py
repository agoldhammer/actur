from openai import AsyncOpenAI

from actur.config.readconf import get_conf_by_key

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=get_conf_by_key("openai")["secret_key"])
    return _client


async def classify_by_title(title):
    user_msg = " ".join(
        [
            "Classify this text as",
            "French Politics, German Politics, Italian Politics, UK Politics,"
            "US Politics, International Affairs, European Union, Finance, Energy,"
            "Crime, Tech, Science, Economy, Immigration, Climate, Industry,",
            "Environment, Security, Defense,",
            "Agriculture, Education, Books, Art, Music, Architecture, History,",
            "Trade, Culture, Sports, Health, Food, Disaster, War, or Other:",
            title,
            ". Reply should consist solely of category, without explanation.",
        ]
    )
    chat = await _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": user_msg},
        ],
    )
    reply = chat.choices[0].message.content  # type: ignore
    return reply


# def main():
#     async def _main():
#         init_db()
#         count = 0
#         tot_tokens = 0
#         arts = await get_arts_in_daterange_from_pubs(["all"], None, None, None, 2, None)
#         async for art in arts:
#             count += 1
#             print(f"Message {count}")
#             title = art["title"]
#             print(title)
#             n_tokens = len(title.split(" "))
#             tot_tokens += n_tokens
#             category = await classify_by_title(title)
#             print(f"ChatGPT: {category}")
#             await asyncio.sleep(0.03)
#             print("...")
#         print("Total tokens: ", tot_tokens)

#     asyncio.run(_main())


# if __name__ == "__main__":
#     main()
