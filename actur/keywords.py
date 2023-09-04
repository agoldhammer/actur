import openai
import time

from actur.config.readconf import get_conf_by_key
from actur.utils.query import get_arts_in_daterange_from_pubs

arts = get_arts_in_daterange_from_pubs(["all"], None, None, None, 2, None)


openai_key = get_conf_by_key("openai")["secret_key"]

openai.api_key = openai_key
count = 0
tot_tokens = 0


def extract_kws_from_summary(summary):
    # message = input("User : ")
    print(summary)
    messages = [{"role": "system", "content": "You are an intelligent assistant."}]
    message = "Extract top 5 keywords from: " + summary
    if message:
        messages.append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    reply = chat.choices[0].message.content  # type: ignore
    print(f"ChatGPT: {reply}")


for art in arts:
    count += 1
    print(f"Message {count}")
    summary = art["summary"]
    n_tokens = len(summary.split(" "))
    tot_tokens += n_tokens
    extract_kws_from_summary(summary)
    time.sleep(1)
    print(f"Current token count: {tot_tokens}")
    print("...")
