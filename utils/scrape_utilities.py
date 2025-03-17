import re
import requests
import tldextract
from urllib3 import Retry
from urllib.parse import urlsplit
from requests.adapters import HTTPAdapter

_REQUESTS_HEADER = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/134.0.0.0"
        "Safari/537.36"
}


def requests_response(url: str, session: requests.Session):
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[502, 503, 504],
        allowed_methods={'POST'},
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, headers=_REQUESTS_HEADER, timeout=(1, 5), stream=True)
        return response

    except requests.ConnectionError or requests.TooManyRedirects as e:
        print("Nelze se připojit k URL. Prosím, zadejte jiné URL. url: ", url, "Exception: ", e)
        return False
    # except requests.Timeout or urllib3.exceptions.MaxRetryError as e:
    #     raise Exception("Vypršel čas připojení. Zkuste znovu. e:", e)
    except Exception as e:
        print("Neznámá chyba. Zkuste znovu nebo zadejte jiné URL. URL:", url, "Exception: e: ", e)
        return False


def check_url_string(url: str):
    try:
        if url is None:
            print("URL.")
            return False
        if len(url) == 0:
            print("Prázdné URL.")
            return False
    except TypeError as e:
        print("Zadejte řetězec ve formě https://www.example.com/. e:", e)
        return False
    except Exception as e:
        print("Zadejte řetězec ve formě https://www.example.com/. e:", e)
        return False

    regex_url = r"^(http|https)://(\w)+([-._]\w+)*\.[a-z]+(/.+)*/?$"
    pattern = re.compile(regex_url, re.MULTILINE | re.IGNORECASE)
    if not pattern.search(url):
        print("Neplatné URL. Zadejte URL znovu ve formě https://www.example.com/.", url)
        return False

    return True


def check_webpage_response(url: str):
    with requests.Session() as session:
        try:
            response = requests_response(url, session)
            if not response:
                return False

            if not response.status_code == 200:
                print("Chyba ve spojení.")
                return False

            if not response.headers['Content-Type'].startswith('text/html'):
                print("Nejedná se o html stránku. Zadejte prosím URL k webové stránce.")
                return False

        except Exception as e:
            print("Exception check_webpage_response(). e:", e)
            return False

        finally:
            if response:
                response.close()

    return True


def get_base_url(url: str):
    if not check_url_string(url):
        return False

    url_parsed = urlsplit(url)
    if not tldextract.extract(url).subdomain:
        base_url = url_parsed.scheme + "://www." + url_parsed.netloc.strip('/')
    else:
        base_url = url_parsed.scheme + "://" + url_parsed.netloc.strip('/')

    return base_url
