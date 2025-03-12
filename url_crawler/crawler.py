import re
from urllib.parse import urljoin

from url_crawler.selenium_scraper import SeleniumScraper
from url_crawler.sitemap_crawler import SitemapCrawler
from utils.scrape_utilities import (
    check_url_string,
    get_base_url,
    requests_response,
)


class LinkCrawler:
    def __init__(self, url: str):
        url.strip()
        if not url.endswith('/'):
            url += '/'
        self.url = url
        self.base_url = None
        self.unvisited_links = set()

    def get_links(self) -> set[str]:
        links = set()

        if not check_url_string(self.url):
            return links

        self.base_url = get_base_url(self.url)
        robots_url = urljoin(self.url, "/robots.txt")
        response = requests_response(robots_url)

        if response:
            if response.status_code == 200:
                regex_url = "^site-?map:\\s*(.+)$"
                pattern = re.compile(regex_url, re.MULTILINE | re.IGNORECASE)
                robots_links = pattern.findall(response.text)
                for link in robots_links:
                    self.unvisited_links.update(link.splitlines())
        else:
            print("No robots.txt found")

        if self.unvisited_links:
            sitemap_crawler = SitemapCrawler(
                self.url,
                self.base_url,
                self.unvisited_links
            )

            links = sitemap_crawler.get_links()
        else:
            sitemap_crawler = SitemapCrawler(
                self.url,
                self.base_url
            )

            links = sitemap_crawler.get_links()

        if not links:
            print("Selenium - Homepage scrape for links.")
            scraper = SeleniumScraper(
                self.url,
                self.base_url
            )
            try:
                scraper.get_links()
                links.update(scraper.get_collected_links())

            except Exception as e:
                print("Selenium scrape error: ", e)

            finally:
                scraper.close()

        return links
