from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium import webdriver
from sys import platform
from selenium.webdriver.support import expected_conditions as EC
from queue import Queue
import logging
import threading
from utils.web_proxy import WebProxy
from utils.singleton import Singleton
from utils.config_center import Config

logger = logging.getLogger(__name__)

class WebDriverPool(metaclass=Singleton):

    def __init__(self):
        config = Config().get_config("crawlers").get("selenium", {}).get("pool", {})
        self.size = config.get("size", 8)
        self.created_proxy_driver_num = 0
        self.created_no_proxy_driver_num = 0
        self.lock = threading.Lock()
        self.queue = Queue(maxsize=self.size)
        # self.page_load_timeout = config.get("page_load_timeout", 10)
        self.page_load_timeout = None
        self.user_agent = config['user_agent']
        self.proxy = WebProxy().get_first_available_proxy_str()

    def __build_options(self, with_proxy=False):
        options = ChromeOptions()
        options.add_argument(f"user-agent={self.user_agent}")
        if not Config().get_global_config("disable_headless"):
            options.add_argument('--headless')
        options.add_argument("--enable-javascript")
        if platform == "linux" or platform == "linux2":
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--no-sandbox")
        preferences = {
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False,
            "download_restrictions": 3
        }
        options.add_experimental_option("prefs", preferences)
        options.add_argument("disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        if with_proxy:
            if not self.proxy:
                raise Exception("no available proxy")
            options.add_argument(f"--proxy-server={self.proxy}")
        return options

    def get_driver(self, with_proxy=False):
        with self.lock:
            if with_proxy:
                if self.created_proxy_driver_num < self.size:
                    self.created_proxy_driver_num += 1
                    driver = webdriver.Chrome(options=self.__build_options(with_proxy=True))
                    if self.page_load_timeout:
                        driver.set_page_load_timeout(self.page_load_timeout)
                    return driver
            else:
                if self.created_no_proxy_driver_num < self.size:
                    self.created_no_proxy_driver_num += 1
                    driver = webdriver.Chrome(options=self.__build_options(with_proxy=False))
                    if self.page_load_timeout:
                        driver.set_page_load_timeout(self.page_load_timeout)
                    return driver
        return self.queue.get()

    def release_driver(self, driver):
        self.queue.put(driver)