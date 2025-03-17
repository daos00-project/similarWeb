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

_MAX_LINKS = 400
_MAX_LINKS_FROM_EACH_SITEMAP = 100


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

    def scrape_links(self) -> set[str]:
        print("unvisited links: ", self.get_unvisited_links())
        links = set()

        while self.unvisited_links and (len(links) < _MAX_LINKS):
            link = self.unvisited_links.pop()
            if link in self.visited_links:
                continue

            self.visited_links.add(link)

            if not bool(urlsplit(link).netloc):
                link = urljoin(self.base_url, link)

            print("Scraping: ", link)

            try:
                response = requests_response(link, self.session)
                if response:
                    if response.status_code == 200:
                        if response.headers['Content-Type'].startswith(('application/xml', 'text/xml')):
                            soup = BeautifulSoup(response.text, "xml")
                            sitemap_elements = soup.find_all("loc")

                            if sitemap_elements:
                                response.close()
                                for element in sitemap_elements:
                                    check_response = requests_response(element.get_text(strip=True), self.session)
                                    if check_response:
                                        if check_response.headers['Content-Type'].startswith(
                                                ('application/xml', 'text/xml')):
                                            reduced_sitemap_elements = sitemap_elements[:_MAX_LINKS_FROM_EACH_SITEMAP]
                                            for sitemap_ele in reduced_sitemap_elements:
                                                self.unvisited_links.add(sitemap_ele.get_text(strip=True))
                                                print("added to unvisited_links: ", sitemap_ele.get_text(strip=True))
                                            break

                                        elif check_response.headers['Content-Type'].startswith('text/html'):
                                            if len(self.unvisited_links) > 0:
                                                reduced_links = sitemap_elements[:_MAX_LINKS_FROM_EACH_SITEMAP]
                                                for link in reduced_links:
                                                    links.add(link.get_text(strip=True))

                                            else:
                                                reduced_links = sitemap_elements[:_MAX_LINKS]
                                                for link in reduced_links:
                                                    links.add(link.get_text(strip=True))
                                            break

                                        else:
                                            print("Exception inside SitemapCrawler, scrape xml. url: ", link,
                                                  "Content-Type: ", check_response.headers['Content-Type'])
                                        check_response.close()

                        elif response.headers['Content-Type'].startswith('text/plain'):
                            text = response.text.strip()
                            txt_links = text.splitlines()
                            if txt_links:
                                if len(self.unvisited_links) > 0:
                                    reduced_links = txt_links[:_MAX_LINKS_FROM_EACH_SITEMAP]
                                    for link in reduced_links:
                                        if not bool(urlsplit(link).netloc):
                                            full_link = urljoin(self.base_url, link)
                                            links.add(full_link.strip())

                                else:
                                    reduced_links = txt_links[:_MAX_LINKS]
                                    for link in reduced_links:
                                        if not bool(urlsplit(link).netloc):
                                            full_link = urljoin(self.base_url, link)
                                            links.add(full_link.strip())

                            else:
                                raise Exception("Exception inside SitemapCrawler, scrape text/plain. url: ", link,
                                                "Content-Type: ", response.headers['Content-Type'])

                        elif response.headers['Content-Type'].startswith('text/html'):
                            soup = BeautifulSoup(response.content, 'lxml')
                            html_links = soup.find_all("loc", string=True)
                            if not html_links:
                                html_links = soup.body.get_text("\n", strip=True).splitlines()

                            if not html_links:
                                raise Exception("Exception inside SitemapCrawler, scrape text/html. url: ", link,
                                                "Content-Type: ", response.headers['Content-Type'])

                            links.update(html_links)

                        else:
                            raise Exception("Exception inside SitemapCrawler, scrape unknown. url: ", link, "Content-Type: ",
                                            response.headers['Content-Type'])
            finally:
                if response:
                    response.close()

        return links
