import re
import time
from collections import Counter
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from urllib.parse import urlsplit, urljoin, urldefrag, urlparse
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.custom_exceptions import ScrapeException
from utils.utilities_responses import check_webpage_response
from utils.utilities_url import get_base_url


class SeleniumScraper:
    def __init__(self, url: str, base_url: str, number_of_htmls: int):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument("--start-maximized")  # set window size on start
        # reduces memory usage and decreases crashes due to /dev/shm partition being too small
        chrome_options.add_argument('--disable-dev-shm-usage')
        # doesn't wait for images to load to begin interactions
        image_preferences = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", image_preferences)
        my_user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
        chrome_options.add_argument(f"--user-agent={my_user_agent}")
        # exclude indication that browser is controlled by automation
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # disables automatic extension installation like screenshot
        chrome_options.add_experimental_option('useAutomationExtension', False)
        # prevents chromium from indicating that its being controlled by automation software
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        try:
            service = webdriver.ChromeService()
            self.driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
        except Exception:
            raise Exception("Could not start web driver. Try again.")

        self.url = url
        self.base_url = base_url
        self.number_of_htmls = number_of_htmls
        self.url_language = None
        self.scraped_links = set()
        self.scraped_htmls = []
        self.collected_internal_links = Counter()

    def scrape_links(self):
        try:
            html_dom, driver_url = self.get_html_dom(self.url)
            if not html_dom:
                return None

            soup = BeautifulSoup(html_dom, "lxml")
            body = soup.find("body")
            if body:
                a_tags = body.find_all("a")
                for a in a_tags:
                    link = a.get('href')

                    if not bool(urlsplit(link).netloc):
                        link = urljoin(self.url, link)

                    if link.startswith("http"):
                        if get_base_url(link) == self.base_url:
                            self.collected_internal_links.update([urldefrag(link).url.strip('/')])

                self.url_language = soup.html.get("lang")
        except Exception:
            pass
        return self.get_collected_internal_links()

    def get_collected_internal_links(self):
        return self.collected_internal_links

    def set_collected_internal_links(self, collected_internal_links: Counter):
        self.collected_internal_links.update(collected_internal_links)

    def scrape_html_documents(self):
        if self.url not in self.scraped_links:
            html_dom, driver_url = self.get_html_dom(self.url)
            if html_dom:
                self.add_html(self.url, driver_url, html_dom)
                if self.number_of_htmls == len(self.scraped_htmls):
                    return
            else:
                raise ScrapeException(self.url)

        # Scrape website domain if not done yet
        if self.base_url not in self.scraped_links:
            try:
                check_webpage_response(self.base_url)
                html_dom, driver_url = self.get_html_dom(self.base_url)
                if html_dom and driver_url not in self.scraped_links:
                    soup = BeautifulSoup(html_dom, "lxml")
                    html_lang = soup.html.get("lang")
                    if html_lang == self.url_language:
                        self.add_html(self.base_url, driver_url, html_dom)
                        if self.number_of_htmls == len(self.scraped_htmls):
                            return

            except Exception:
                pass

        if not self.collected_internal_links:
            return

        given_url_path_segments = self.get_path_segments(self.url)
        if given_url_path_segments == 0:
            self.scrape_variety(given_url_path_segments, variety=False)
        else:
            self.scrape_variety(given_url_path_segments, variety=True)
            if len(self.scraped_htmls) < self.number_of_htmls:
                self.scrape_variety(given_url_path_segments, variety=False)

        return

    def scrape_variety(self, given_url_path_segments, variety):
        similar = False
        urls_to_scrape = []
        for url, count in self.collected_internal_links.most_common():
            if url in self.scraped_links:
                continue

            # In case of high variety mode, if path of url has higher depth or has similar path (path segments until
            # before last segment of both URL are same), skip.
            if variety:
                path_segments = self.get_path_segments(url)
                if len(path_segments) == 1:
                    pass
                elif len(path_segments) > len(given_url_path_segments):
                    continue
                elif len(given_url_path_segments) <= 1:
                    if len(path_segments) > 1:
                        continue
                elif len(given_url_path_segments) > 1:
                    potential_urls = self.scraped_links.copy()
                    potential_urls.update(urls_to_scrape)
                    for stored_url in potential_urls:
                        stored_path_segments = self.get_path_segments(stored_url)
                        if len(stored_path_segments) == 0:
                            continue

                        if path_segments[:-1] == stored_path_segments[:-1]:
                            similar = True
                            break

                    if similar:
                        similar = False
                        continue

            try:
                check_webpage_response(url)
            except Exception:
                continue

            urls_to_scrape.append(url)
            if len(urls_to_scrape) >= (self.number_of_htmls - len(self.scraped_htmls)):
                self.multiple_tab_scraping(urls_to_scrape)
                if len(self.scraped_htmls) >= self.number_of_htmls:
                    return
                else:
                    urls_to_scrape = []

        # if all collected_internal_links were iterated and there are links left in urls_to_scrape to scrape
        if urls_to_scrape:
            self.multiple_tab_scraping(urls_to_scrape)

        return


    def get_all_html_documents(self) -> list:
        return self.scraped_htmls

    def get_html_dom(self, url: str):
        try:
            self.driver.get(url)

            total_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if total_height > 5000:
                total_height = 5000
            self.driver.set_window_size(1920, total_height)

            time.sleep(1)
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
        except Exception:
            # Retry.
            try:
                self.driver.get(url)
                time.sleep(1)
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )
            except Exception:
                if url in self.collected_internal_links:
                    del self.collected_internal_links[url]
                return False, None

        return self.driver.page_source, self.driver.current_url

    def multiple_tab_scraping(self, urls_to_scrape):
        original_tab = self.driver.current_window_handle
        try:
            for url in urls_to_scrape:
                try:
                    self.driver.get(url)
                    WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'body'))
                    )
                    break
                except Exception as e:
                    if url in self.collected_internal_links:
                        del self.collected_internal_links[url]
                    urls_to_scrape.remove(url)

            if len(urls_to_scrape) > 1:
                for url in urls_to_scrape[1:]:
                    current_tab = self.driver.current_window_handle
                    try:
                        self.driver.switch_to.new_window('tab')
                        self.driver.get(url)
                        WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.TAG_NAME, 'body'))
                        )
                    except Exception as e:
                        self.driver.close()
                        self.driver.switch_to.window(current_tab)
                        urls_to_scrape.remove(url)
                        if url in self.collected_internal_links:
                            del self.collected_internal_links[url]

            for idx, window_handle in enumerate(self.driver.window_handles):
                self.driver.switch_to.window(window_handle)
                if len(self.scraped_htmls) >= self.number_of_htmls:
                    break

                url = urls_to_scrape[idx]
                driver_url = self.driver.current_url
                if driver_url and driver_url in self.scraped_links:
                    continue

                html_dom = self.driver.page_source
                if not html_dom:
                    continue

                soup = BeautifulSoup(html_dom, "lxml")
                html_lang = soup.html.get("lang")
                if html_lang == self.url_language:
                    self.add_html(url, driver_url, html_dom)

        except Exception:
            pass

        finally:
            for window_handle in self.driver.window_handles:
                if window_handle != original_tab:
                    self.driver.switch_to.window(window_handle)
                    self.driver.close()
            self.driver.switch_to.window(original_tab)

        return

    def add_html(self, url: str, driver_url: str, html_dom):
        self.scraped_htmls.append(f"{url}\n" + self.reduce_html_dom(html_dom))
        self.scraped_links.add(url.strip('/'))
        self.scraped_links.add(driver_url.strip('/'))

    def close_driver(self):
        self.driver.quit()

    @staticmethod
    def reduce_html_dom(html_dom: str) -> str:
        reduced_html_dom = BeautifulSoup(html_dom, "lxml")
        for extract_tag in reduced_html_dom(
                ["link", "script", "noscript", "style", "svg", "path", "animate", "animateMotion", "iframe"]):
            extract_tag.extract()

        for tag in reduced_html_dom.find_all(True):
            tag.attrs.pop("class", None)
            tag.attrs.pop("style", None)
            tag.attrs.pop("target", None)
            tag.attrs.pop("onclick", None)
            tag.attrs.pop("src", None)

        comments = reduced_html_dom.findAll(text=lambda text: isinstance(text, Comment))
        [comment.extract() for comment in comments]

        for img_tag in reduced_html_dom.find_all("img"):
            copy = img_tag.copy_self()
            for attr in copy.attrs.keys():
                if attr != "alt":
                    del img_tag.attrs[attr]

        reduced_html_dom = reduced_html_dom.prettify()
        return re.sub(pattern=r'^\s+', repl='', string=reduced_html_dom, flags=re.MULTILINE)

    @staticmethod
    def get_path_segments(url: str) -> list[str]:
        parsed_url = urlparse(url)
        path_segments = [p for p in parsed_url.path.split('/') if p]
        return path_segments
