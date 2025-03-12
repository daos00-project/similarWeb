import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urljoin
from utils.scrape_utilities import requests_response

_SITEMAPS_LINKS: set[str] = {
    "sitemap.xml", "sitemap.xml.gz",
    "sitemap1.xml", "sitemap1.xml.gz",
    "sitemap_index.xml", "sitemap_index.xml.gz",
    "sitemap-index.xml", "sitemap-index.xml.gz",
    "sitemap/index.xml", "sitemap/index.xml.gz",
    "sitemap/index.html", "sitemap/index.php",
    "sitemap.html", "sitemap.txt", "sitemap.php",
    "google-sitemap.html", "google-sitemap.php", "google-sitemap.txt",
    "sitemap/sitemap-index.xml", "sitemap/sitemap-index.xml.gz",
}

_MAX_LINKS = 5000


class SitemapCrawler:
    def __init__(self, url: str, base_url: str, session: requests.Session, unvisited_links: set = None):
        if unvisited_links is None:
            self.unvisited_links = _SITEMAPS_LINKS.copy()
        else:
            self.unvisited_links = unvisited_links

        self.url = url
        self.base_url = base_url
        self.session = session
        self.visited_links = set()

    def get_unvisited_links(self) -> set[str]:
        return self.unvisited_links

    def get_links(self) -> set[str]:
        print("unvisited links: ", self.get_unvisited_links())
        links = set()

        while self.unvisited_links and len(links) < _MAX_LINKS:
            link = self.unvisited_links.pop()
            if link in self.visited_links:
                continue

            self.visited_links.add(link)

            if not bool(urlsplit(link).netloc):
                link = urljoin(self.base_url, link)

            print("Scraping: ", link)

            response = requests_response(link, self.session)
            if response.status_code == 200:
                if response.headers['Content-Type'].startswith(('application/xml', 'text/xml')):
                    soup = BeautifulSoup(response.text, "xml")
                    sitemap_elements = soup.find_all("loc")

                    if sitemap_elements:
                        response = requests_response(sitemap_elements[0].get_text(strip=True), self.session)

                        if response.headers['Content-Type'].startswith(('application/xml', 'text/xml')):
                            for sitemap_ele in sitemap_elements:
                                self.unvisited_links.add(sitemap_ele.get_text(strip=True))
                                print("added to unvisited_links: ", sitemap_ele.get_text(strip=True))
                        elif response.headers['Content-Type'].startswith(('text/html', 'application/pdf')):
                            for link in sitemap_elements:
                                links.add(link.get_text(strip=True))
                        else:
                            raise Exception("Exception inside SitemapCrawler, scrape xml. url: ", link,
                                            "Content-Type: ", response.headers['Content-Type'])

                elif response.headers['Content-Type'].startswith('text/plain'):
                    text = response.text.strip()
                    txt_links = text.splitlines()
                    regex_url_both = r"^(http|https)://(\w)+([-\._]\w+)*(\.[a-z]+)+(/[^.]+)*(.[a-z]+)*/?$|^(/?[^.\/]+)*(.[a-z]+)?/?$"
                    pattern = re.compile(regex_url_both, re.MULTILINE | re.IGNORECASE)
                    if txt_links:
                        for line in txt_links:
                            if pattern.match(line.strip()):
                                if not bool(urlsplit(line).netloc):
                                    full_link = urljoin(self.base_url, line)
                                    links.add(full_link.strip())
                    else:
                        raise Exception("Exception inside SitemapCrawler, scrape text/plain. url: ", link,
                                        "Content-Type: ", response.headers['Content-Type'])

                elif response.headers['Content-Type'].startswith('text/html'):
                    soup = BeautifulSoup(response.content, 'lxml')
                    html_links = soup.find_all(string=True)
                    links.update(html_links)

                else:
                    raise Exception("Exception inside SitemapCrawler, scrape unknown. url: ", link, "Content-Type: ",
                                    response.headers['Content-Type'])

        return links
