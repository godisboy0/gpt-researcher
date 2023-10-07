from abc import ABC, abstractmethod
from llms.prompt_provider import PromptProvider
from llms.base_llm_util import LLMUtil
from llms.report_outline_generator import SubTopic
import logging
from components import ExpandedQuestion
from utils.cache_manager import cache_result
from utils.time_usage_record import time_usage

logger = logging.getLogger(__name__)


class QuestionExpander(ABC):

    @abstractmethod
    def expand(self, task_id: str, role_prompt: str, sub_topic: SubTopic) -> ExpandedQuestion:
        """
        use to expand the search queries for the question.

        Args:
            role_prompt (str): the role prompt for the question
            sub_topic (SubTopic): sub topic of the topic user asked
            so we can always split big topic into sub topics, and we always generate the search queries for the leaf topic.
        """
        pass


def key_gen(*args, **kwargs) -> str:
    sub_topic: SubTopic = kwargs.get("sub_topic") if kwargs.get(
        "sub_topic") else args[3]
    return f"{sub_topic.topic}:::{sub_topic.sub_topic}"


class DefaultQuestionExpander(QuestionExpander):

    def __init__(self, prompt_provider: PromptProvider, llm_util: LLMUtil) -> None:
        self.prompt_provider = prompt_provider
        self.llm_util = llm_util

    def __str__(self) -> str:
        return f"prompt_provider: {self.prompt_provider.__class__.__name__}, llm_util: {self.llm_util.__class__.__name__}"

    def __extract_expanded_question(self, role_prompt: str, sub_topic: SubTopic, response: str) -> ExpandedQuestion:
        import re
        import json
        pattern = r"\[.*\]"
        match = re.search(pattern, response, re.DOTALL)
        if not match:
            logger.warning(
                f"failed to expand sub_topic: {sub_topic} using role prompt: {role_prompt}, expander: {self}, llm raw response: {response}")
            return None
        return ExpandedQuestion(sub_topic, json.loads(match.group()))

    @cache_result("expanded_questions", cache_class=ExpandedQuestion, key_gen=key_gen)
    @time_usage
    def expand(self, task_id: str, role_prompt: str, sub_topic: SubTopic) -> ExpandedQuestion:
        logger.info(
            f"expanding sub_topic: {sub_topic} using role prompt: {role_prompt}, expander: {self}")

        prompt = self.prompt_provider.search_queries_prompt(sub_topic)

        messages = [
            {
                "role": "system",
                "content": role_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        response = self.llm_util.get_smart_result(
            messages=messages,
            task_id=task_id
        )
        logger.debug(
            f"expanded sub_topic: {sub_topic} using role prompt: {role_prompt}, expander: {self}, expanded raw question: {response}")

        return self.__extract_expanded_question(role_prompt, sub_topic, response)
