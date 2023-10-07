# 定义一个装饰器方法，用于缓存函数的返回值

import os


from typing import Callable, Type
from components import CacheAble
import logging
import json
import enum
import hashlib
import threading

logger = logging.getLogger(__name__)

lock = threading.Lock()
cache = {}


class CacheType(enum.Enum):
    """
    cache type
    """
    Generator = "generator",
    Object = "object"


def default_key_gen(*args, **kwargs) -> str:
    return hashlib.md5(
        (str(args) + str(kwargs)).encode("utf-8")).hexdigest()

def get_file_path(task_id: str, cache_file: str) -> str:
    cache_path = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), "output", task_id)
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    file_path = os.path.join(cache_path, cache_file + ".json")
    return file_path

def get_or_create_cache(task_id: str, cache_file: str, key: str) -> str | list[str] | None:
    with lock:
        file_path = get_file_path(task_id, cache_file)

        if task_id not in cache:
            cache[task_id] = {}
        if cache_file not in cache[task_id]:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    cache[task_id][cache_file] = json.loads(f.read())
            else:
                with open(file_path, "w") as f:
                    f.write("{}")
                cache[task_id][cache_file] = {}
        return cache[task_id][cache_file].get(key, None)


def update_and_save_cache(task_id: str, cache_file: str, key: str, value: str) -> None:
    with lock:
        file_path = get_file_path(task_id, cache_file)

        if task_id not in cache:
            cache[task_id] = {}
        if cache_file not in cache[task_id]:
            cache[task_id][cache_file] = {}
        cache[task_id][cache_file][key] = value
        with open(file_path, "w") as f:
            f.write(json.dumps(cache[task_id][cache_file], indent=4, ensure_ascii=False))


def cache_result(cache_file: str, cache_class: Type[CacheAble],
                 cache_type: CacheType = CacheType.Object, key_gen: Callable = default_key_gen) -> Callable:
    if cache_type not in [CacheType.Generator, CacheType.Object]:
        raise ValueError(
            "cache_type must be CacheType.Generator or CacheType.Object")
    if key_gen:
        if not callable(key_gen):
            raise ValueError("key_gen must be callable")

    if cache_type == CacheType.Generator:
        def decorator_generate(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                task_id = args[1] if len(args) > 0 else kwargs.get("task_id")
                if not isinstance(task_id, str):
                    return func(*args, **kwargs)
                # 使用所有的args和kwargs，str，md5, 作为cache的key
                key = key_gen(*args, **kwargs)
                r_num = 0
                result_list = get_or_create_cache(
                    task_id, cache_file, key) or []
                if result_list:
                    for r in result_list:
                        r_num += 1
                        logger.debug(f"generator, loading cache for {key}")
                        yield cache_class.deserialize(cache_class, r)

                # 如果到了这一步，说明没有文件，或者没有找到对应的key，或者key对应的值用完了，执行函数
                new_num = 0
                for r in func(*args, **kwargs):
                    if new_num < r_num:
                        new_num += 1
                        continue
                    logger.debug(f"generator, generating new cache for {key}")
                    result_list.append(r.serialize())
                    update_and_save_cache(task_id, cache_file, key, result_list)
                    yield r
            return wrapper
        return decorator_generate
    else:
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                task_id = args[1] if len(args) > 0 else kwargs.get("task_id")
                if not isinstance(task_id, str):
                    return func(*args, **kwargs)
                key = key_gen(*args, **kwargs)
                result = get_or_create_cache(task_id, cache_file, key)
                if result:
                    return cache_class.deserialize(cache_class, result)
                # 如果到了这一步，说明没有文件，或者没有找到对应的key，执行函数
                result = func(*args, **kwargs)
                logger.debug(f"object, generating new cache for {key}")
                if result:
                    update_and_save_cache(task_id, cache_file, key, result.serialize())
                return result
            return wrapper
        return decorator
