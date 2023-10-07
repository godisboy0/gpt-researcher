# 一个装饰器方法，统计所有的函数运行时间，并将结果保存到文件中

import time
import threading
import os
import inspect
import json

lock = threading.Lock()

def __format_time(t: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))

def __write_file(task_id: str, func, start_time: int, end_time: int):
    with lock:
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output",
                                 task_id, "time_usage.json")
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        if not os.path.exists(file_path):
            with open(file_path, "w+") as f:
                f.write('[')
        with open(file_path, "r+") as f:
            f.seek(0, 2)
            size = f.tell()
            if size > 2:
                # not new file, write leading ','
                f.seek(size - 1)
                f.truncate()
                f.write(',')

            f.write(
                json.dumps({
                    "func_name": f"{inspect.getmodule(func).__name__}.{func.__name__}",
                    "start_time": __format_time(start_time),
                    "end_time": __format_time(end_time),
                    "time_usage": int(end_time - start_time)
                }, ensure_ascii=False, indent=4) + ']'
            )


def time_usage(func):
    def wrapper(*args, **kwargs):
        task_id = kwargs.get("task_id") if kwargs.get("task_id") else args[1]
        if not isinstance(task_id, str):
            return
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        __write_file(task_id, func, start_time, end_time)
        return result

    return wrapper

if __name__ == "__main__":
    
    @time_usage
    def test(task_id: str, i: int = 0):
        print("test: ", i)

    for i in range(10):
        test(task_id="test", i=i)