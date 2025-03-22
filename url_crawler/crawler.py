import re
import requests
from collections import Counter
from urllib.parse import urljoin, urlsplit
from url_crawler.selenium_scraper import SeleniumScraper
from url_crawler.sitemap_crawler import SitemapCrawler
from utils.scrape_utilities import (
    check_url_string,
    get_base_url,
    requests_response,
    check_webpage_response,
)

_MIN_REQUIRED_LINKS = 5


class LinkCrawler:
    def __init__(self, url: str):
        clean_url = url.strip()
        parsed_url = urlsplit(clean_url)
        reformatted_url = get_base_url(clean_url) + parsed_url.path
        if parsed_url.query:
            reformatted_url += "?" + parsed_url.query

        self.url = reformatted_url
        self.base_url = None
        self.unvisited_links = set()
        self.collected_internal_links = Counter()

    def scrape_htmls(self):

        if not check_url_string(self.url):
            return False
        if not check_webpage_response(self.url):
            return False

        self.base_url = get_base_url(self.url)

        scraper = SeleniumScraper(
            self.url,
            self.base_url
        )

        self.collected_internal_links.update(self.scrape_links(scraper))
        scraper.set_collected_internal_links(self.collected_internal_links)

        scraper.scrape_html_documents()
        html_documents = scraper.get_all_html_documents()
        scraper.close_driver()

        return html_documents

    def scrape_links(self, scraper) -> Counter:
        try:
            self.collected_internal_links.update(scraper.scrape_links())

        except Exception as e:
            print(f"Selenium scrape error: {e}. Trying again.")
            try:
                self.collected_internal_links.update(scraper.scrape_links())

            except Exception as e:
                print(f"Selenium scrape error: {e}. Get links from sitemaps.")

        if len(self.collected_internal_links) < _MIN_REQUIRED_LINKS:
            with requests.Session() as session:
                robots_url = urljoin(self.base_url, "/robots.txt")
                response = requests_response(robots_url, session)

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
