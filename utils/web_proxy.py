from utils.config_center import Config
from utils.singleton import Singleton
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ProxySetting:
    
    def __init__(self, type, host, user, password):
        self.type = type
        self.host = host
        self.user = user
        self.password = password

    def get_proxy_str(self):
        if self.user is None:
            return f'{self.type}://{self.host}'
        else:
            return f'{self.type}://{self.user}:{self.password}@{self.host}'
        
    def __str__(self) -> str:
        return self.get_proxy_str()
    
    def __repr__(self) -> str:
        return self.get_proxy_str()

class WebProxy(metaclass=Singleton):

    def __init__(self):
        self.config = Config()
        self.proxy = self.config.get_config('proxy')
        if 'http' in self.proxy:
            self.proxy['http'] = ProxySetting('http', self.proxy['http']['host'], self.proxy['http'].get('user', None), self.proxy['http'].get('password', None))

        if 'https' in self.proxy:
            self.proxy['https'] = ProxySetting('https', self.proxy['https']['host'], self.proxy['https'].get('user', None), self.proxy['https'].get('password', None))

        if 'socks5' in self.proxy:
            self.proxy['socks5'] = ProxySetting('socks5', self.proxy['socks5']['host'], self.proxy['socks5'].get('user', None), self.proxy['socks5'].get('password', None))
        
        logger.debug(f"Proxy setting: {self.proxy}")

    def get_http_proxy(self) -> Optional[ProxySetting]:
        return self.proxy.get('http', None)
    
    def get_https_proxy(self) -> Optional[ProxySetting]:
        return self.proxy.get('https', None)
    
    def get_socks5_proxy(self) -> Optional[ProxySetting]:
        return self.proxy.get('socks5', None)
    
    def get_first_available_proxy_str(self, order: list[str] = ["socks5", "https", "http"]) -> Optional[str]:
        for proxy_type in order:
            proxy = self.proxy.get(proxy_type, None)
            if proxy:
                return proxy.get_proxy_str()
        return None