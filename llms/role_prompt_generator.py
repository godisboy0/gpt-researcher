from abc import ABC, abstractmethod
from llms.prompt_provider import PromptProvider
from llms.base_llm_util import LLMUtil
from components import RolePrompt
import logging
from utils.cache_manager import cache_result
from utils.time_usage_record import time_usage

logger = logging.getLogger(__name__)


class RolePromptGenerator(ABC):
    """
    auto generate role prompt for the specific question.
    LLM will determine the agent type and role based on the question and the topic.
    """

    @abstractmethod
    def generate(self, task_id: str, topic: str) -> RolePrompt:
        """
        use to generate system prompt for the specific agent type.
        see GPT4RolePromptGenerator.get_role_prompt for an example
        return should be a dict with the following format:
        { 
            "agent":  "📈 Business Analyst Agent",
            "agent_role_prompt": "You are an experienced AI business analyst assistant. bla bla..."
        } 
        """
        pass


class DefaultRolePromptGenerator(RolePromptGenerator):

    def __init__(self, prompt_provider: PromptProvider, llm_util: LLMUtil) -> None:
        self.prompt_provider = prompt_provider
        self.llm_util = llm_util

    @cache_result("role_prompts", cache_class=RolePrompt, key_gen=lambda *args, **kwargs: kwargs.get("topic") if kwargs.get("topic") else args[2])
    @time_usage
    def generate(self, task_id: str, topic: str) -> RolePrompt:
        logger.info(
            f"generating role prompt for topic: {topic}, generator: {self.__class__.__name__}")
        messages = [
            {
                "role": "system",
                "content": self.prompt_provider.auto_agent_prompt()
            },
            {
                "role": "user",
                "content": topic
            }
        ]
        response = self.llm_util.get_smart_result(
            messages=messages,
            task_id=task_id
        )
        logger.info(
            f"generated role prompt for topic: {topic}, generator: GPT4RolePromptGenerator, role prompt: {response}")

        import re
        import json
        pattern = r"\{.*\}"
        match = re.search(pattern, response, re.DOTALL)
        if not match:
            raise ValueError(
                f"failed to generate role prompt for topic: {topic}, generator: GPT4RolePromptGenerator, role prompt: {response}")

        result = json.loads(match.group(0))
        if 'agent' not in result or 'agent_role_prompt' not in result:
            raise ValueError(
                f"failed to generate role prompt for topic: {topic}, generator: GPT4RolePromptGenerator, role prompt: {response}")

        return RolePrompt(agent=result['agent'], agent_role_prompt=result['agent_role_prompt'])
