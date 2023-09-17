import textwrap
from colorama import Fore, Style
from .summary_parser import summary_parse


def display_article(article, summary_flag: bool):
    print(f"{Fore.YELLOW}{article['pubname']}: {article['pubdate']}")
    print(article["title"])
    print(f"Category: {article['cat']}")
    # print(article)
    print(20 * "-")
    print(f"{Style.RESET_ALL}")
    if summary_flag:
        summary, image_source = summary_parse(article["summary"])
        text = textwrap.fill(
            text=summary,
            width=80,
            initial_indent="+->",
            subsequent_indent=5 * " ",
        )
        print(text)
        if image_source != "":
            src = textwrap.fill(
                text="Image source: " + image_source,
                width=80,
                initial_indent="**--->",
                subsequent_indent=7 * " ",
            )
            print(src)

    print(f"\n{Fore.LIGHTMAGENTA_EX}{article['link']}{Style.RESET_ALL}\n")
    print(20 * "-")


def display_articles(cursor, summary_flag: bool):
    for article in cursor:
        display_article(article, summary_flag)
