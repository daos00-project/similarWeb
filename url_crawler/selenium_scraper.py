import time
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlsplit, urljoin, urldefrag
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.scrape_utilities import get_base_url


class SeleniumScraper:
    def __init__(self, url: str, base_url: str):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.page_load_strategy = 'normal'
        chrome_options.add_argument("--start-maximized")
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
        self.visited_links = set()
        self.collected_links = set()

    def get_links(self) -> set[str]:
        print("Scraping: ", self.base_url)
        try:
            self.driver.get(self.base_url)
            time.sleep(2)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            html_content = self.driver.page_source
            # add scrape and save html method

            soup = BeautifulSoup(html_content, "lxml")
            body = soup.find("body")
            if body:
                a_tags = body.find_all("a")
                for a in a_tags:
                    link = a.get('href')

                    if not bool(urlsplit(link).netloc):
                        link = urljoin(self.base_url, link)
                        print("Joined link: ", link)

                    if get_base_url(link) == self.base_url:
                        self.collected_links.add(urldefrag(link).url)
                    else:
                        print("Link does not match: ", link)
            else:
                print("No <body> tag found")

        except Exception as e:
            raise Exception("Exception inside SeleniumCrawler, couldn't visit page. url: ", self.base_url, "except: ", e)

        return self.get_collected_links()

    def get_collected_links(self):
        return self.collected_links

    def close(self):
        self.driver.quit()
