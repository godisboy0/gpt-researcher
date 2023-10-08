import json
import os
from utils.singleton import Singleton

def merge_dict(dict1, dict2):
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            merge_dict(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1

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
            config2 = self.__load_config(os.path.join(os.path.dirname(
                os.path.dirname(__file__)), 'config', 'config.private.json'))
            self.config = merge_dict(self.config, config2)
        self.check_config()

    def set_global_config(self, key: str, value):
        """
        set global config
        """
        self.config['global'][key] = value
    
    def get_global_config(self, key: str):
        """
        get global config
        """
        return self.config['global'].get(key)

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
        if 'global' in self.config:
            raise Exception("global config should not be set in config file")
        if 'global' not in self.config:
            self.config['global'] = {}
        pass


    def __load_config(self, config_path) -> dict:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config