import re
import tldextract
from urllib.parse import urlsplit


def reformat_url(url):
    parsed_url = urlsplit(url)
    reformatted_url = get_base_url(url) + parsed_url.path
    if parsed_url.query:
        reformatted_url += "?" + parsed_url.query
    return reformatted_url


def check_url_string(url: str):
    regex_url = r"^(http|https)://((--|[-._])?\w+)*(/[^\s]+)*/?$"
    pattern = re.compile(regex_url, re.MULTILINE | re.IGNORECASE)
    if not pattern.search(url):
        return False

    return True


def get_base_url(url: str):
    if not check_url_string(url):
        return False

    url_parsed = urlsplit(url)
    if not tldextract.extract(url).subdomain:
        if url_parsed.netloc.startswith('www.'):
            base_url = url_parsed.scheme + "://" + url_parsed.netloc.strip('/')
        else:
            base_url = url_parsed.scheme + "://www." + url_parsed.netloc.strip('/')
    else:
        base_url = url_parsed.scheme + "://" + url_parsed.netloc.strip('/')

    return base_url
