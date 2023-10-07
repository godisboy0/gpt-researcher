"""
this file is used to generate the outline of the report.
implementations can use LLM for the generation, or just let the user to write the outline.
"""

from abc import ABC, abstractmethod
from llms.prompt_provider import PromptProvider
from llms.base_llm_util import LLMUtil
from components import ReportOutline, SubTopic
from utils.cache_manager import cache_result
from utils.time_usage_record import time_usage

class ReportOutlineGenerator(ABC):

    @abstractmethod
    def generate(self, task_id: str, role_prompt: str, topic: str) -> ReportOutline:
        """
        generate the outline of the report

        Args:
            role_prompt (str): the role prompt.
            question (str): the question
        """
        pass


class DefaultOutlineGenerator(ReportOutlineGenerator):

    def __init__(self, prompt_provider: PromptProvider, llmutil: LLMUtil) -> None:
        self.prompt_provider = prompt_provider
        self.llm_util = llmutil

    @cache_result("report_outlines", cache_class=ReportOutline, key_gen=lambda *args, **kwargs: kwargs.get("topic") if kwargs.get("topic") else args[3])
    @time_usage
    def generate(self, task_id: str, role_prompt: str, topic: str) -> ReportOutline:
        prompt = self.prompt_provider.outline_prompt(topic)
        response = self.llm_util.get_smart_result([
            {
                "role": "system",
                "content": role_prompt
            },
            {
                "role": "user",
                "content": prompt
            }], task_id=task_id)

        return self.parse_response(topic, response)

    def parse_response(self, topic: str, response: str) -> ReportOutline:
        import re
        try:
            # 提取 response 中的内容
            res = re.findall(r"```(.*)```", response, re.S)
            if not res:
                first_second_heading = response.find("#")
                if first_second_heading == -1:
                    raise ValueError("generate outline failed, please check the response, topic: {topic} response: {response}".format(
                        topic=topic, response=response))
                response = response[first_second_heading:]
            else:
                response = res[0]

            res = response.split("##")
            # 丢弃标题
            top_heading = res[0].strip()
            res = ["##" + i.strip() for i in res if i.strip()][1:]
            # 提取每一个问题的标题和简要描述
            sub_topics = []
            for single in res:
                single = single.split("\n")
                sub_topic = single[0].strip()
                word_suggestion = None
                matches = re.findall(r"\d+", sub_topic.strip())
                if matches:
                    word_suggestion = int(matches[0])

                describe = "\n".join(single[1:]).strip()
                sub_topics.append(
                    SubTopic(topic, sub_topic, describe, word_suggestion))
            return ReportOutline(topic, top_heading, response, sub_topics)
        except Exception as e:
            raise ValueError("generate outline failed, please check the response, question: {question} response: {response}".format(
                question=topic, response=response)) from e
