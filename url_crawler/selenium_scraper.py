import time
from collections import Counter
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlsplit, urljoin, urldefrag, urlparse
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.scrape_utilities import get_base_url, check_webpage_response

_MAX_HTMLS_TO_SCRAPE = 5


class SeleniumScraper:
    def __init__(self, url: str, base_url: str):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--disable-dev-shm-usage')
        image_preferences = {
            "profile.managed_default_content_settings.images": 2
        }
        chrome_options.add_experimental_option("prefs", image_preferences)
        my_user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
        chrome_options.add_argument(f"--user-agent={my_user_agent}")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        service = webdriver.ChromeService()
        self.driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        self.url = url
        self.base_url = base_url
        self.scraped_links = []
        self.scraped_htmls = []
        self.collected_internal_links = Counter()

    def scrape_links(self) -> Counter:
        print("Scraping: ", self.url)
        try:
            html_dom = self.get_html_dom(self.url)
            if not html_dom:
                print("Error Selenium scrape_links.")
                return self.get_collected_internal_links()

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
                            self.collected_internal_links[urldefrag(link).url.strip('/')] += 1
                        else:
                            print("Not an internal link:", link, ", base of link:", get_base_url(link), "base_url",
                                  self.base_url)

                self.scraped_htmls.append(f"{self.url}\n" + self.reduce_html_dom(html_dom))
                self.scraped_links.append(self.url.strip('/'))

        except Exception as e:
            raise Exception("Exception inside SeleniumCrawler, couldn't visit page. url: ", self.base_url, "except: ",
                            e)

        return self.get_collected_internal_links()

    def get_collected_internal_links(self):
        return self.collected_internal_links

    def set_collected_internal_links(self, sitemap_links: Counter):
        self.collected_internal_links.update(sitemap_links)
        return

    def scrape_html_documents(self, variety=True) -> bool:
        """
        Scrape variety of links with varied path and then in LLM inference
        mention inside prompt to give priority to the scraped html document of a given URL.
        """
        # Homepage should contain the most information about the site -> scrape html
        if self.base_url not in self.scraped_links:
            if check_webpage_response(self.base_url):
                html_dom = self.get_html_dom(self.base_url)
                if not html_dom:
                    print("Empty html. Skipping")

                reduced_html_dom = f"{self.base_url}\n" + self.reduce_html_dom(html_dom)
                self.scraped_htmls.append(reduced_html_dom)
                self.scraped_links.append(self.base_url.strip('/'))
                print("HTML Added for: ", self.base_url)

        urls_to_scrape = []
        given_url_path_segments = self.get_path_segments(self.url)
        similar = False
        for url, count in self.collected_internal_links.most_common(200):
            print(f"{url}: {count} mentions")

            if url in self.scraped_links:
                continue

            # In case of high variety mode, if path of url has higher depth or has similar path (path segments until
            # before last segment are same), skip.
            if variety:
                path_segments = self.get_path_segments(url)
                if len(path_segments) == 1:
                    pass
                elif len(given_url_path_segments) <= 1:
                    if len(path_segments) > 1:
                        continue
                elif len(given_url_path_segments) > 1:
                    potential_urls = self.scraped_links.copy()
                    potential_urls.extend(urls_to_scrape)
                    for stored_url in potential_urls:
                        stored_path_segments = self.get_path_segments(stored_url)
                        if len(stored_path_segments) == 0:
                            continue

                        if len(path_segments) > len(stored_path_segments) or path_segments[:-1] == stored_path_segments[:-1]:
                            similar = True
                            break

            if similar:
                similar = False
                continue

            if not check_webpage_response(url):
                continue

            urls_to_scrape.append(url)
            if len(urls_to_scrape) > (_MAX_HTMLS_TO_SCRAPE - len(self.scraped_links)):
                break

        if len(urls_to_scrape) > (_MAX_HTMLS_TO_SCRAPE - len(self.scraped_links)):
            self.multiple_tab_scraping(urls_to_scrape)
            if len(self.scraped_htmls) > 4:
                return True

        if len(self.scraped_htmls) < 6 and variety is True:
            print("Not enough HTMLs, scraping URLs with less variety.")
            self.scrape_html_documents(variety=False)

        return True

    def get_all_html_documents(self) -> list:
        return self.scraped_htmls

    def get_html_dom(self, url: str):
        print("Scraping url:", url)
        try:
            self.driver.get(url)

            total_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if total_height > 5000:
                total_height = 5000
            self.driver.set_window_size(1920, total_height)

            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

        except Exception as e:
            print(f"Selenium navigate error: {e}. Trying again.")
            try:
                self.driver.get(self.base_url)
                time.sleep(1)
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )
            except Exception as e:
                print(f"Selenium navigate error: {e}. Skipping.")
                return False

        return self.driver.page_source

    def multiple_tab_scraping(self, urls_to_scrape):
        print("Multiple tabs scraping urls:", urls_to_scrape)
        try:
            self.driver.get(urls_to_scrape[0])
            self.driver.set_window_size(1920, 5000)

            for url in urls_to_scrape[1:]:
                self.driver.switch_to.new_window('tab')
                self.driver.get(url)

            for idx, window_handle in enumerate(self.driver.window_handles):
                self.driver.switch_to.window(window_handle)
                if len(self.scraped_htmls) >= 5:
                    break

                html_dom = self.driver.page_source
                if not html_dom:
                    continue

                url = urls_to_scrape[idx]
                reduced_html_dom = f"{url}\n" + self.reduce_html_dom(html_dom)
                self.scraped_htmls.append(reduced_html_dom)
                self.scraped_links.append(url.strip('/'))
                print("HTML added for:", url)

        except Exception as e:
            print(f"fast Selenium navigate error: {e}. Skipping.")
            return False

        return True

    def close_driver(self):
        self.driver.quit()

    @staticmethod
    def reduce_html_dom(html_dom: str) -> str:
        reduced_html_dom = BeautifulSoup(html_dom, "lxml")
        for extract_tag in reduced_html_dom(
                ["link", "script", "noscript", "style", "svg", "canvas", "path", "animate", "animateMotion", "iframe"]):
            extract_tag.extract()

        for tag in reduced_html_dom.find_all(True):
            tag.attrs.pop("class", None)

        for img_tag in reduced_html_dom.find_all("img"):
            copy = img_tag.copy_self()
            for attr in copy.attrs.keys():
                if attr != "alt":
                    del img_tag.attrs[attr]

        return reduced_html_dom.prettify()

    @staticmethod
    def get_path_segments(url: str) -> list[str]:
        parsed_url = urlparse(url)
        path_segments = [p for p in parsed_url.path.split('/') if p]
        return path_segments
