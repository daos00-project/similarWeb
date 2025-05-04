class ExceptionUnknown(Exception):
    """Exception raised when an unknown error occurs"""

    def __init__(self, url, e):
        self.url = url
        self.e = e
        super().__init__(f"'Unknown error with url: {self.url}. Please enter a different URL or try again later.\n"
                         f"Exception message for developer: {self.e}")


class InvalidWebpage(Exception):
    """Exception raised when URL is not a HTML webpage"""

    def __init__(self, url):
        self.url = url
        super().__init__(f"'{self.url}' is not a valid HTML webpage. Please enter a URL to a webpage.")


class WebpageConnectionError(Exception):
    """Exception raised when requests couldn't connect to webpage"""

    def __init__(self, url):
        self.url = url
        super().__init__(
            f"Could not connect to '{self.url}'. Please enter a different URL.")


class WebpageResponseError(Exception):
    """Exception raised when requests couldn't connect to webpage"""

    def __init__(self, url):
        self.url = url
        super().__init__(
            f"Could not obtain response from '{self.url}'. Content might be blocked. Please enter a different URL or try again later.")


class WebpageCodeError(Exception):
    """Exception raised when requests couldn't connect to webpage"""

    def __init__(self, url):
        self.url = url
        super().__init__(
            f"'{self.url}' not satified. Please enter a different URL or try copying URL from the address bar in your browser.")


class ScrapeException(Exception):
    """Exception raised when scraper fails to scrape webpage"""

    def __init__(self, url):
        self.url = url
        super().__init__(f"Could not extract HTML from '{self.url}'. Please enter a different URL or try again later.")
