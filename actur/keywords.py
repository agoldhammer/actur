import time

import openai

from actur.config.readconf import get_conf_by_key
from actur.utils.query import get_arts_in_daterange_from_pubs


def extract_kws_from_summary(summary):
    # message = input("User : ")
    print(summary)
    messages = [{"role": "system", "content": "You are an intelligent assistant."}]
    message = (
        "Extract, as a comma-separated list of strings, top 5 keywords from: " + summary
    )
    if message:
        messages.append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    reply = chat.choices[0].message.content  # type: ignore
    print(f"ChatGPT: {reply}")


def extract_kws_from_title(title):
    # message = input("User : ")
    messages = [{"role": "system", "content": "You are an intelligent assistant."}]
    message = " ".join(
        [
            "Classify this text as",
            "French Politics, German Politics, Italian Politics, UK Politics,"
            "US Politics, International Affairs, European Union,"
            "Crime, Tech, Science, Economy, Immigration"
            "Trade, Culture, Sports, Health, Food, Disaster, War, or Other:",
            title,
            ". Reply should consist solely of category, without explanation.",
        ]
    )
    if message:
        messages.append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    reply = chat.choices[0].message.content  # type: ignore
    print(f"ChatGPT: {reply}")


def main():
    openai.api_key = get_conf_by_key("openai")["secret_key"]
    count = 0
    tot_tokens = 0
    arts = get_arts_in_daterange_from_pubs(["all"], None, None, None, 2, None)
    for art in arts:
        count += 1
        print(f"Message {count}")
        title = art["title"]
        print(title)
        n_tokens = len(title.split(" "))
        tot_tokens += n_tokens
        extract_kws_from_title(title)
        time.sleep(0.05)
        # print(f"Current token count: {tot_tokens}")
        print("...")
    print("Total tokens: ", tot_tokens)


if __name__ == "__main__":
    main()
