import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urljoin

from config.config import MAX_LINKS_TO_SCRAPE
from utils.utilities_responses import requests_response

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
        collected_links = set()

        while self.unvisited_links and len(collected_links) < MAX_LINKS_TO_SCRAPE:
            link = self.unvisited_links.pop()
            if link in self.visited_links:
                continue

            self.visited_links.add(link)
            if not bool(urlsplit(link).netloc):
                link = urljoin(self.base_url, link)

            response = None
            try:
                response = requests_response(link, self.session)
                if response and response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    collected_links.update(self.process_response(response, content_type))
            except Exception:
                pass
            finally:
                if response:
                    response.close()

        return collected_links

    def process_response(self, response: requests.Response, content_type: str) -> set[str]:
        if content_type.startswith(('application/xml', 'text/xml')):
            return self.handle_xml_content(response)
        elif content_type.startswith('text/plain'):
            return self.handle_text_content(response)
        elif content_type.startswith('text/html'):
            return self.handle_html_content(response)
        else:
            return set()

    def handle_xml_content(self, response: requests.Response) -> set[str]:
        links = set()
        soup = BeautifulSoup(response.text, "xml")
        sitemap_elements = soup.find_all("loc")

        if not sitemap_elements:
            return links

        for element in sitemap_elements:
            url = element.get_text(strip=True)
            try:
                check_response = requests_response(url, self.session)
            except:
                continue

            # If obtained response, add all and break loop. Assumption is, that whole file contains same type URL.
            if check_response:
                if check_response.headers['Content-Type'].startswith(('application/xml', 'text/xml')):

                    for sitemap_ele in sitemap_elements:
                        self.unvisited_links.add(sitemap_ele.get_text(strip=True))
                    break

                elif check_response.headers['Content-Type'].startswith('text/html'):
                    reduced_links = sitemap_elements[:MAX_LINKS_TO_SCRAPE]
                    for link in reduced_links:
                        links.add(link.get_text(strip=True))
                    break

                check_response.close()

        return links

    def handle_text_content(self, response: requests.Response) -> set[str]:
        text = response.text.strip()
        txt_links = text.splitlines()
        links = set()

        if txt_links:
            reduced_links = txt_links[:MAX_LINKS_TO_SCRAPE]
            for link in reduced_links:
                if not bool(urlsplit(link).netloc):
                    full_link = urljoin(self.base_url, link)
                    links.add(full_link.strip())

        return links

    def handle_html_content(self, response: requests.Response) -> set[str]:
        soup = BeautifulSoup(response.content, 'lxml')
        html_links = soup.find_all("loc", string=True)

        if not html_links:
            html_links = soup.body.get_text("\n", strip=True).splitlines()

        if not html_links:
            return set()
        
        return set(html_links)
