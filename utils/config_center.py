import json
import os
from utils.singleton import Singleton


class Config(metaclass=Singleton):

    def __init__(self) -> None:
        """
        load config file.
        check if config/config.private.json exists, if not, load config/config.default.json
        """
        if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.default.json')):
            self.config = self.__load_config(os.path.join(os.path.dirname(
                os.path.dirname(__file__)), 'config', 'config.default.json'))
        if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.private.json')):
            self.config.update(self.__load_config(os.path.join(os.path.dirname(
                os.path.dirname(__file__)), 'config', 'config.private.json')))
        self.check_config()

    def get_config(self, key) -> dict:
        """
        return a dict of giving key, if not found, return empty dict
        always deep copy
        """
        if key in self.config:
            return self.config[key].copy()
        else:
            return {}

    def check_config(self):
        # TODO: check config integrity
        pass


    def __load_config(self, config_path) -> dict:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config