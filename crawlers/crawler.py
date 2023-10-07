from components import CrawledPage
from utils.config_center import Config
from abc import ABC, abstractmethod
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webdriver import WebElement
from typing import Callable
from bs4 import BeautifulSoup
import logging
from .selenium_driver_pool import WebDriverPool

logger = logging.getLogger(__name__)


class Crawler(ABC):

    @abstractmethod
    def crawl(self, url) -> CrawledPage:
        """
        crawl a page, return a CrawledPage object
        """
        pass

    @abstractmethod
    def get_pattern_prefix(self) -> str:
        """
        return a prefix of the url pattern, for example, if the crawler is used to crawl
        https://www.example.com/abc/def/123.html, then the prefix may be 
        https://www.example.com/abc/def/ or https://www.example.com/abc
        implements can use prefix such as localfile:// to indicate the crawler is used to read local files
        if prefix from different crawler matches, the crawler with longer prefix will be used
        """
        pass


class SeleniumCrawler(Crawler):

    def __init__(self):
        self.config = Config().get_config("crawlers").get("selenium", {})
        logger.info(f"using selenium crawler with config: {self.config}")
        self.use_proxy = self.config.get('use_proxy', False)
        self.driver_pool = WebDriverPool()
    
    def crawl(self, url) -> CrawledPage:
        driver = self.driver_pool.get_driver(self.use_proxy)
        try:
            logger.info(f"crawling {url} using selenium")

            driver.get(url)
            WebDriverWait(driver, 20).until(
                self._get_page_waiting_condition()
            )
            page_source = self._get_page_source(driver=driver)
            soup = BeautifulSoup(page_source, "html.parser")

            for script in soup(["script", "style"]):
                script.extract()

            text = self._get_text(soup)

            logger.debug(
                f"page text length get by selenium: {len(text)}, first 100 characters: {text[:100]}")

            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip()
                    for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)
            return CrawledPage(url, driver.title, text)
        finally:
            self.driver_pool.release_driver(driver)


    def _get_page_source(self, driver: Chrome) -> str:
        """
        get the page source, this method can be overrided to change the behavior
        """
        return driver.execute_script("return document.body.outerHTML;")

    def _get_text(self, soup):
        """
        parse the html and get the text, this method can be overrided to change the behavior
        """
        text = ""
        tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'p']
        for element in soup.find_all(tags):  # Find all the <p> elements
            text += element.text + "\n\n"
        return text

    def _get_page_waiting_condition(self) -> Callable[[Chrome], WebElement]:
        """
        under most circumstances, the page is loaded when the body tag is loaded, or other tag is loaded
        implements can override this method to change the waiting condition, this should be sufficient for most cases
        """
        return EC.presence_of_element_located((By.TAG_NAME, "body"))

    def get_pattern_prefix(self) -> str:
        """
        this is the fallback crawler, so it should have the shortest prefix
        """
        return ""
