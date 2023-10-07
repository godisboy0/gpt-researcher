from search.search_engine import SearchEngine, SearchResult
from utils.config_center import Config
from utils.web_proxy import WebProxy
import logging
from typing import Generator
from utils.cache_manager import cache_result, CacheType
from utils.time_usage_record import time_usage

logger = logging.getLogger(__name__)
try:
    from duckduckgo_search import DDGS
except ImportError:
    raise ImportError(
        "duckduckgo_search module not found. Please install it with 'pip install duckduckgo_search'")

proxy = {}
if WebProxy().get_socks5_proxy():
    proxy['http://'] = WebProxy().get_socks5_proxy().get_proxy_str()
    proxy['https://'] = WebProxy().get_socks5_proxy().get_proxy_str()
else:
    if WebProxy().get_http_proxy():
        proxy['http://'] = WebProxy().get_http_proxy().get_proxy_str()
    if WebProxy().get_https_proxy():
        proxy['https://'] = WebProxy().get_https_proxy().get_proxy_str()

ddgs = DDGS(proxies=proxy)


class DuckDuckGoEngine(SearchEngine):

    def __init__(self):
        self.config = Config().get_config('duckduckgo')
        self.region = self.config.get('region', 'wt-wt')
        self.safesearch = self.config.get('safesearch', 'moderate')

    def get_name(self) -> str:
        return 'duckduckgo'

    @cache_result("search_results", cache_class=SearchResult, cache_type=CacheType.Generator, key_gen=lambda *args, **kwargs: kwargs.get("query") if kwargs.get("query") else args[2])
    @time_usage
    def search(self, task_id: str, query: str, start_num: int = 0) -> Generator[SearchResult, None, None]:
        logger.debug(
            f"Searching '{query}' on DuckDuckGo, region: {self.region}, safesearch: {self.safesearch}")
        if not query:
            logger.warning("Empty query for DuckDuckGo")
            return []
        try:
            results = ddgs.text(query, region=self.region,
                                safesearch=self.safesearch)
            if not results:
                logger.warning(f"No results for '{query}' on DuckDuckGo")
                return
            num_returned = 0
            for result in results:
                if num_returned < start_num:
                    num_returned += 1
                    continue
                num_returned += 1
                yield SearchResult(result.get('href'), result.get('title'), result.get('body'), query)


        except Exception as e:
            logger.exception(f"Error searching '{query}' on DuckDuckGo: {e}")
            return
