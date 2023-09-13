from typing import Tuple

import bs4


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
