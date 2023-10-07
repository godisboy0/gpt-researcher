from pipeline.pipeline_factory import create_pipeline
import logging
from llms.openai_util import DefaultLLMUtil
from pipeline.pipeline import generate_task_id
import os


def search(topic):
    # setup logging
    log_file_path = os.path.join(os.path.dirname(
        __file__), "output", generate_task_id(topic), "search.log")
    if not os.path.exists(os.path.dirname(log_file_path)):
        os.makedirs(os.path.dirname(log_file_path))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_path, encoding="utf-8")
        ]
    )
    p = create_pipeline()
    return p.do_research(topic)


def calculate_price(topic):
    return DefaultLLMUtil().get_bill(generate_task_id(topic))


if __name__ == "__main__":
    # topic = "How to evaluate the novel: The Lord of the Rings series?"
    topic = "How to evaluate Alfred Hictchcock and his movies?"
    # search(topic)
    print(calculate_price(topic))