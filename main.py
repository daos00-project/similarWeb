import time
from url_crawler.crawler import LinkCrawler


def main():
    # Urls to try
    # failing urls
    # url = "https://developer.mozilla.org/sitemaps/en-us/sitemap.xml.gz"
    # url = "https://www.imdb.com/sitemap.xml"
    # url = "https://qweoiuajsf.com/"

    # working urls
    # url = "http://ravel-net.org"
    # url = "https://www.faithfacts.org"
    # url = "https://www.wiska.co.uk"
    # url = "https://imdb.com/" # no sitemap inside robots.txt but sitemap exists
    # url = "https://www.vse.cz/"
    # url = "https://fis.vse.cz/"
    # url = "https://www.vse.cz/informace-o-vse/profil-skoly/vyrocni-zpravy/"
    # url = "https://kalendar.vse.cz/event/show?date=7145&web=fis.vse.cz"
    # url = "https://docs.spring.io/spring-framework/docs/3.0.x/reference/beans.html"
    url = "https://www.scrapfly.io/"
    # url = "https://www.uradprace.cz/" # no robots.txt and sitemaps
    obj = LinkCrawler(url)

    html_documents = obj.scrape_htmls()
    if not html_documents:
        print("No HTML documents found. Try again or use another URL.")
        return 0

    print("No. of HTMLS: ", len(html_documents))
    for idx, html in enumerate(html_documents):
        with open(f"page{idx}-eager.text", "w", encoding="utf-8") as file:
            file.write(html)

    # LLM inference

if __name__ == '__main__':
    t0 = time.time()
    main()
    t1 = time.time()
    res = t1 - t0
    print("Execution time: ", res)
