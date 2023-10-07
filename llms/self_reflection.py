"""
to be honest, I'm not sure if what happens here can be called self-reflection...
But I believe this will help the report perform better.
"""

from abc import ABC, abstractmethod
import logging
from llms.prompt_provider import PromptProvider
from llms.base_llm_util import LLMUtil
from components import SubTopic, DeterminResult
from utils.cache_manager import cache_result
from utils.time_usage_record import time_usage
import hashlib

logger = logging.getLogger(__name__)


class SelfReflecter(ABC):

    @abstractmethod
    def determin_relavance(self, task_id: str, role_prompt: str, sub_topic: SubTopic, content: str) -> DeterminResult:
        """
        determin the relavance of the response to the question.

        Args:
            role_prompt (str): the role prompt
            question (str): the question
            response (str): the response

        Returns:
            bool: True if the response is relavant to the question, False otherwise.
        """
        pass

def key_gen(*args, **kwargs) -> str:
    sub_topic: SubTopic = kwargs.get("sub_topic") if kwargs.get(
        "sub_topic") else args[3]
    content: str = kwargs.get("content") if kwargs.get(
        "content") else args[4]
    return f"{sub_topic.topic}:::{sub_topic.sub_topic}:::{hashlib.md5(content.encode()).hexdigest()}"

class DefaultSelfReflecter(SelfReflecter):

    def __init__(self, prompt_provider: PromptProvider, llm_utils: LLMUtil) -> None:
        self.llm_util = llm_utils
        self.prompt_provider = prompt_provider

    @cache_result("determin_results", cache_class=DeterminResult, key_gen=key_gen)
    @time_usage
    def determin_relavance(self, task_id: str, role_prompt: str, sub_topic: SubTopic, content: str) -> DeterminResult:
        # I'm not sure if gpt-3.5 will be able to handle this... well, it just do well...
        prompt = self.prompt_provider.self_reflection_prompt(
            sub_topic, content)
        response = self.llm_util.get_fast_result([
            {
                "role": "system",
                "content": role_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ], task_id=task_id)
        # try to extract a boolean value from the response
        if response.lower() == 'yes' or response.lower().find('yes') != -1:
            return DeterminResult(content, True)
        elif response.lower() == 'no' or response.lower().find('no') != -1:
            return DeterminResult(content, False)
        else:
            logger.warning(
                f"failed to determin relavance of response: {response}")
            return DeterminResult(content, False)
