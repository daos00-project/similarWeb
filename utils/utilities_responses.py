import requests
from urllib3 import Retry
from requests.adapters import HTTPAdapter
from utils.custom_exceptions import (
    WebpageConnectionError,
    ExceptionUnknown,
    InvalidWebpage, WebpageResponseError, WebpageCodeError
)

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
        if not response:
            return False

        return response

    except (requests.ConnectionError, requests.TooManyRedirects, requests.Timeout):
        raise WebpageConnectionError(url)
    except Exception as e:
        raise ExceptionUnknown(url, e)


def check_webpage_response(url: str):
    with requests.Session() as session:
        response = None
        try:
            response = requests_response(url, session)

            if not response:
                raise WebpageResponseError(url)

            if not response.status_code == 200:
                raise WebpageCodeError(url)

            if not response.headers.get('Content-Type', '').startswith('text/html'):
                raise InvalidWebpage(url)
        except Exception as e:
            raise Exception(e)
        finally:
            if response:
                response.close()

    return True
