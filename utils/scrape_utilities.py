import re
import requests
from urllib.parse import urlsplit

_REQUESTS_HEADER = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/134.0.0.0"
        "Safari/537.36"
}


def get_base_url(url: str):
    url_parsed = urlsplit(url)
    return url_parsed.scheme + "://" + url_parsed.netloc


def check_url_string(url: str):
    try:
        if url is None:
            print("URL.")
            return False
        if len(url) == 0:
            print("Prázdné URL.")
            return False
    except TypeError:
        print("Zadejte řetězec ve formě https://www.example.com/.")
        return False

    regex_url = r"^(http|https)://(\w)+([-\._]\w+)*(\.[a-z]+)+(/[^.]+)*(.[a-z]+)*/?$"
    pattern = re.compile(regex_url, re.MULTILINE | re.IGNORECASE)
    if not pattern.search(url):
        print("Neplatné URL. Zadejte URL znovu ve formě https://www.example.com/.")
        return False

    return True


def requests_response(url: str):
    try:
        response = requests.get(url, headers=_REQUESTS_HEADER)
        return response

    except requests.ConnectionError or requests.TooManyRedirects as e:
        raise Exception("Nelze se připojit k URL. Prosím, zadejte jiné URL. e: ", e)
    except requests.Timeout as e:
        raise Exception("Vypršel čas připojení. Zkuste znovu. ", e)
    except requests.HTTPError as e:
        raise Exception("Chyba odpovědi hlavičky HTTP. Zkuste znovu. ", e)
    except requests.URLRequired as e:
        raise Exception("Neplatný URL. ", e)
    except Exception as e:
        raise Exception("Neznámá chyba. Zkuste znovu nebo zadejte jiné URL. Exception: ", e)
