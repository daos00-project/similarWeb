import re
import requests
from collections import Counter
from urllib.parse import urljoin
from model.url_crawler.selenium_scraper import SeleniumScraper
from model.url_crawler.sitemap_crawler import SitemapCrawler
from utils.utilities_responses import requests_response
from utils.utilities_url import get_base_url


class Crawler:
    def __init__(self, url: str, number_of_htmls: int):
        self.url = url
        self.base_url = get_base_url(self.url)
        self.number_of_htmls = number_of_htmls

        try:
            self.scraper = SeleniumScraper(
                self.url,
                self.base_url,
                self.number_of_htmls
            )
        except Exception as e:
            raise Exception(e)

        self.unvisited_links = set()
        self.collected_internal_links = Counter()

    def scrape_htmls(self):
        self.scraper.set_collected_internal_links(self.collected_internal_links)

        self.scraper.scrape_html_documents()
        self.scraper.close_driver()

        return self.scraper.get_all_html_documents()

    def crawl_links(self) -> Counter:
        try:
            self.collected_internal_links.update(self.scraper.scrape_links())
        except Exception:
            pass

        if len(self.collected_internal_links) < self.number_of_htmls:
            with requests.Session() as session:
                robots_url = urljoin(self.base_url, "/robots.txt")

                try:
                    response = requests_response(robots_url, session)
                    if response:
                        if response.status_code == 200:
                            regex_url = "^site-?map:\\s*(.+)$"
                            pattern = re.compile(regex_url, re.MULTILINE | re.IGNORECASE)
                            robots_links = pattern.findall(response.text)
                            for link in robots_links:
                                self.unvisited_links.update(link.splitlines())
                except Exception:
                    pass

                if self.unvisited_links:
                    sitemap_crawler = SitemapCrawler(
                        self.url,
                        self.base_url,
                        session,
                        self.unvisited_links
                    )

                    self.collected_internal_links.update(sitemap_crawler.scrape_links())
                else:
                    sitemap_crawler = SitemapCrawler(
                        self.url,
                        self.base_url,
                        session
                    )

                    self.collected_internal_links.update(sitemap_crawler.scrape_links())

        return self.get_collected_internal_links()

    def get_collected_internal_links(self):
        return self.collected_internal_links
