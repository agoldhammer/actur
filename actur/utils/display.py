import textwrap
from colorama import Fore, Style
from .summary_parser import summary_parse


def display_article(article):
    print(f"{Fore.YELLOW}{article['pubname']}: {article['pubdate']}")
    print(article["title"])
    print(20 * "-")
    print(f"{Style.RESET_ALL}")
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
    print(20 * "-")
