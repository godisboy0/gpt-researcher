"""
this tool is used to load class from a module.
useful when you want to load several sub class from a base class in a module 
when you are not concerned about the name of the sub class.
such as loading all crawlers from crawlers.crawler
"""

import importlib
import inspect


def load_class_from_module(module_name: str, base_class: type) -> list[type]:

    module = importlib.import_module(module_name)
    classes = []
    for _, cls in inspect.getmembers(module, inspect.isclass):
        if cls.__module__ == module_name and issubclass(cls, base_class) and cls != base_class:
            classes.append(cls)
    return classes