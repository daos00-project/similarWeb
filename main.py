from url_crawler.crawler import LinkCrawler


def main():
    # Urls to try
    # url = "http://ravel-net.org"
    # url = "https://www.faithfacts.org"
    # url = "https://www.wiska.co.uk"
    # url = "https://imdb.com/"
    # url = "https://developer.mozilla.org/sitemaps/en-us/sitemap.xml.gz"
    # url = "https://vse.cz/"
    url = "https://www.vse.cz/informace-o-vse/profil-skoly/vyrocni-zpravy/"
    # url = "https://example.com/"
    # url = "https://scrapfly.io/"
    # url = "https://www.uradprace.cz/"
    obj = LinkCrawler(url)

    pages_to_scrape = obj.get_links()
    print(pages_to_scrape)


if __name__ == '__main__':
    main()
