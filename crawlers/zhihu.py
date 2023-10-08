"""
you know, for zhihu
"""
from crawlers.crawler import SeleniumCrawler
from components import CrawledPage
from utils.config_center import Config
import os
from sys import platform
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import json
import time
from bs4 import BeautifulSoup
import logging
import threading

logger = logging.getLogger(__name__)


class ZhihuCrawler(SeleniumCrawler):

    def __init__(self):
        self.user_agent = Config().get_config("crawlers").get(
            "selenium", {}).get("pool", {}).get("user_agent")
        self.refer = "https://duckduckgo.com/"
        self.lock = threading.Lock()

        self.cookie_file = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), "temp", "zhihu.cookie.json")
        if not os.path.exists(os.path.dirname(self.cookie_file)):
            os.makedirs(os.path.dirname(self.cookie_file))
        if not os.path.exists(self.cookie_file):
            with open(self.cookie_file, "w") as f:
                f.write("{}")
        self.loaded_cookie = self.__get_fresh_cookie_from_file()
        super().__init__()

    def __build_options(self) -> ChromeOptions:
        options = ChromeOptions()
        if self.user_agent:
            options.add_argument(f"user-agent={self.user_agent}")
        options.add_argument("--enable-javascript")
        preferences = {
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False,
            "download_restrictions": 3
        }
        options.add_experimental_option("prefs", preferences)
        options.add_argument("disable-blink-features=AutomationControlled")
        if platform == "linux" or platform == "linux2":
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--no-sandbox")
        return options

    def __get_fresh_cookie_from_file(self) -> list[dict[str, str]]:
        with open(self.cookie_file, "r") as f:
            cookie = json.load(f)
        # 假设一天有效期
        if self.__cookie_fresh(cookie):
            return cookie
        else:
            return None

    def __cookie_fresh(self, cookie: dict) -> bool:
        return cookie and cookie.get('write_time') and cookie.get('write_time') > time.time() - 4 * 60 * 60

    def __get_or_create_cookie(self):
        with self.lock:
            if self.__cookie_fresh(self.loaded_cookie):
                return self.loaded_cookie.get("cookie")

            driver = webdriver.Chrome(options=self.__build_options())
            driver.get("https://www.zhihu.com/signin?next=%2F")
            while True:
                if driver.current_url == "https://www.zhihu.com/" or driver.current_url == "https://www.zhihu.com":
                    break
                time.sleep(1)
            cookie = driver.get_cookies()
            self.loaded_cookie = {
                "cookie": cookie, "write_time": time.time()
            }
            driver.quit()
            with open(self.cookie_file, "w") as f:
                json.dump(self.loaded_cookie, f, indent=4, ensure_ascii=False)

            return cookie

    def crawl(self, url) -> CrawledPage:
        driver = self.driver_pool.get_driver()
        try:
            cookie = self.__get_or_create_cookie()
            driver.get("https://www.zhihu.com")
            for c in cookie:
                if c['domain'] == ".zhihu.com":
                    driver.add_cookie(
                        {"name": c['name'], "value": c['value'], "domain": c['domain']})
            driver.get(url)
            WebDriverWait(driver, 20).until(
                self._get_page_waiting_condition()
            )
            driver.delete_all_cookies()
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
            if text.strip() == "" or text.find("系统监测到您的网络环境存在异常，为保证您的正常访问，请点击下方验证按钮进行验证。在您验证完成前，该提示将多次出现") != -1:
                logger.warning("zhihu crawler blocked by zhihu")
                raise Exception("zhihu crawler blocked by zhihu")
            return CrawledPage(url, driver.title, text)
        finally:
            self.driver_pool.release_driver(driver)

    def get_pattern_prefix(self) -> str:
        return "https://www.zhihu.com/"


class ZhihuZhuanlanCrawler(ZhihuCrawler):

    def __init__(self):
        super().__init__()

    def get_pattern_prefix(self) -> str:
        return "https://zhuanlan.zhihu.com/"
