import bs4
from typing import Tuple


def summary_parse(summary: str) -> Tuple[str, str]:
    """split article summary into text and image source;


    Args:
        summary (str): article summary text

    Returns:
        Tuple[str, str]: summary_text, image_source
    """
    soup = bs4.BeautifulSoup(summary, "html.parser")
    if soup.find() is None:
        return summary, ""
    else:
        img = soup.find("img")
        par = soup.find("p")
        if type(img) is bs4.Tag:
            src = img["src"]
        else:
            src = ""
        if type(src) is not str:
            src = ""
        if type(par) is bs4.Tag:
            summ = par.get_text()
        else:
            summ = ""
        # print(summ, src)
        return summ, src


# # summ1 = '<img src="https://sz-delivery.imgix.net/2022/06/07/52989cee-a52c-4d0f-b9a1-d06e9e93148d.jpeg?rect=0%2C0%2C1200%2C900&amp;width=208&amp;auto=format&amp;q=60" /><p>Unsere Autorin verspürt beim Anblick eines Videos aus dem besetzten Wassyliwka Mitleid und Ekel und amüsiert sich über ein Detail. Notizen aus der Ukraine.</p>'
# # summ2 = "<p>" + summ1 + "</p>"
# # summ3 = "plain text"
# def tryit(text):
#     # dbif.init_db("mongodb://elite.local")
#     # db = dbif.get_db()
#     # art = db.articles.find_one({"pubname": "SZ"})
#     # summtext = art["summary"]
#     # print(summtext)
#     # soup = bs4.BeautifulSoup(text, "html.parser")
#     # if soup.find() is None:
#     #     print("No tags")
#     #     print("text:", text)
#     # else:
#     #     print("Soup:-----")
#     #     img = soup.find("img")
#     #     par = soup.find("p")
#     #     if type(img) is bs4.Tag:
#     #         print("img:", img["src"])
#     #     if type(par) is bs4.Tag:
#     #         print("par:", par.get_text())
#     #     print("----------\n")
#     par, src = summary_parse(text)
#     print("Par:", par, "Src:", src)


# def main():
#     tryit(summ1)
#     tryit(summ2)
#     tryit(summ3)


# if __name__ == "__main__":
#     main()
