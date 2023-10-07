from crawlers.crawler import Crawler, CrawledPage
from utils.singleton import Singleton
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.config_center import Config
from utils.class_loader import load_class_from_module
import logging
from typing import Generator
from utils.cache_manager import cache_result
from utils.time_usage_record import time_usage

logger = logging.getLogger(__name__)


class CrawlerManager(metaclass=Singleton):

    def __init__(self):
        # 按 crawler.get_pattern_prefix() 长度逆序排序
        config = Config()
        module_name = config.get_config("crawlers").get(
            "global", {}).get("module_name", [])
        disabled = Config().get_config("crawlers").get("disabled", [])

        crawlers = []
        for base_dir in module_name:
            crawlers.extend(load_class_from_module(base_dir, Crawler))
        crawlers = [x() for x in crawlers if x.__name__ not in disabled]
        crawlers.sort(key=lambda crawler: len(
            crawler.get_pattern_prefix()), reverse=True)
        self.crawlers: list[Crawler] = crawlers
        self.default_executor = ThreadPoolExecutor(max_workers=20)

    def batch_crawl(self, task_id: str, urls: list[str], executor: ThreadPoolExecutor = None) -> Generator[CrawledPage, None, None]:
        """
        batch crawl a list of urls, return a dict of CrawledPage objects
        """
        logger.info(f"batch_crawl {len(urls)} urls")
        if not urls or not [x for x in urls if x]:
            return {}

        urls = set([x for x in urls if x])

        if not executor:
            executor = self.default_executor
        futures = []
        for url in urls:
            futures.append(executor.submit(self.crawl, task_id, url))

        for future in as_completed(futures):
            try:
                page = future.result()
                yield page
            except Exception as e:
                logger.exception(f"error when batch_crawl: {e}")
                continue

    @cache_result("crawled_pages", cache_class=CrawledPage, key_gen=lambda *args, **kwargs: kwargs.get("url") if kwargs.get("url") else args[2])
    @time_usage
    def crawl(self, task_id: str, url: str) -> CrawledPage:
        """
        crawl a single url, return a CrawledPage object
        """
        clawer = self.get_crawler(url)
        logger.info(f"crawl {url} with {clawer.__class__.__name__}")
        try:
            return clawer.crawl(url)
        except Exception as e:
            logger.exception(
                f"error when crawl {url} with {clawer.__class__.__name__}: {e}")
            return None

    def get_crawler(self, url: str) -> Crawler:
        """
        return the crawler that matches the url
        """
        for crawler in self.crawlers:
            if url.startswith(crawler.get_pattern_prefix()):
                return crawler
        """since we have a default crawler, this should never happen"""
        raise Exception(f"no crawler matched url: {url}")
