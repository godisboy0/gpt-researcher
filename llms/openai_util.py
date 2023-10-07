from llms.base_llm_util import LLMUtil
from utils.config_center import Config
from typing import Generator
from utils.web_proxy import WebProxy
import json
import logging
import os
from components import LLMTokenBill, TokenType, TokenUsage, TokenPrice
try:
    import openai
    # import tiktoken
except ImportError:
    raise ImportError(
        "OpenAI is not installed. Please install it by running `pip install openai`")
logger = logging.getLogger(__name__)


class DefaultLLMUtil(LLMUtil):

    def __init__(self) -> None:
        self.config = Config().get_config("llms").get("openai", {})
        if not self.config.get('api_key'):
            raise ValueError(
                "openai api key is not set, please provide in config file")

        openai.api_key = self.config['api_key']
        if self.config.get('api_base'):
            openai.api_base = self.config['api_base']
        if self.config.get('use_proxy', False):
            openai.proxy = WebProxy().get_first_available_proxy_str()
        if self.config.get('price'):
            self.price = [TokenPrice.deserialize(TokenPrice, p) for p in self.config['price']]
        else:
            self.price = []

    def get_smart_result(self, messages, temperature=0.2, max_tokens=None, **kwargs) -> str:
        model = self.__get_model_for_smart(messages)
        return self.__get_result(model, messages, temperature, max_tokens, **kwargs)

    def get_smart_stream_result(self, messages, temperature=0.2, max_tokens=None, **kwargs) -> Generator[str, None, None]:
        model = self.__get_model_for_smart(messages)
        for r in self.__get_stream_result(model, messages, temperature, max_tokens, **kwargs):
            yield r

    def get_fast_result(self, messages, temperature=0.2, max_tokens=None, **kwargs) -> str:
        model = self.__get_model_for_fast(messages)
        return self.__get_result(model, messages, temperature, max_tokens, **kwargs)

    def get_fast_stream_result(self, messages, temperature=0.2, max_tokens=None, **kwargs) -> Generator[str, None, None]:
        model = self.__get_model_for_fast(messages)
        for r in self.__get_stream_result(model, messages, temperature, max_tokens, **kwargs):
            yield r

    def split_for_fast(self, content: str) -> list[str]:
        this_level = [content]
        next_level = []
        while True:
            all_ok = True
            for c in this_level:
                token_num = self.__num_tokens_from_string(c, "cl100k_base")
                if token_num > 12000:
                    # 二分文本
                    all_ok = False
                    half_num = len(c)//2
                    next_level.extend([c[:half_num], c[half_num:]])
                else:
                    next_level.append(c)
            this_level = next_level
            next_level = []
            if all_ok:
                break
        return this_level

    def split_for_smart(self, content: str) -> list[str]:
        """
        if 32k can not hold, we give up and let it be 😭
        """
        return [content]
    
    def get_bill(self, task_id: str) -> LLMTokenBill:
        path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'output', task_id, 'token_use.json')
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            token_use = json.load(f)
        usage: list[TokenUsage] = []
        for model_key in ["gpt-4-32k", "gpt-4-0613", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-0613"]:
            if model_key in token_use:
                usage.append(TokenUsage(
                    model_key, TokenType.Completion, token_use[model_key]['completion_tokens']))
                usage.append(TokenUsage(
                    model_key, TokenType.Prompt, token_use[model_key]['prompt_tokens']))
        bill = LLMTokenBill(usage, self.price)
        token_use['bill'] = bill.serialize()
        with open(path, 'w') as f:
            json.dump(token_use, f, ensure_ascii=False, indent=4)
        return bill

    def __get_result(self, model, messages, temperature=0, max_tokens=None, **kwargs) -> str:
        logger.debug(
            f"getting result from model: {model}, messages: {str(messages)[:200]}, max_tokens: {max_tokens}, temperature: {temperature}")

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            stream=False,
            temperature=temperature
        )
        self.__record_token_use(kwargs.get("task_id"), model, response)
        logger.debug(f"response: {response}")
        # will work fine with non ascii characters
        return f"""{response['choices'][0].message["content"]}"""

    def __get_stream_result(self, model, messages,  temperature=0, max_tokens=None, **kwargs) -> Generator[str, None, None]:
        logger.debug(
            f"getting stream result from model: {model}, messages: {str(messages)[:200]}, max_tokens: {max_tokens}, temperature: {temperature}")

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
            temperature=temperature
        )

        for chunk in response:
            yield f"""{chunk["choices"][0].message["delta"]}"""
        self.__record_token_use(kwargs.get("task_id"), model, response)

    def __record_token_use(self, task_id: str, model: str, response: dict):
        if task_id is None:
            return
        path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'output', task_id, 'token_use.json')
        if not os.path.exists(path):
            token_use = {}
        else:
            with open(path, 'r') as f:
                token_use = json.load(f)
        old_num_for_model = token_use.get(model, {})
        completion_tokens = old_num_for_model.get(
            'completion_tokens', 0) + response['usage']['completion_tokens']
        prompt_tokens = old_num_for_model.get(
            'prompt_tokens', 0) + response['usage']['prompt_tokens']
        total_tokens = old_num_for_model.get(
            'total_tokens', 0) + response['usage']['total_tokens']
        this_time = {
            'completion_tokens': response['usage']['completion_tokens'],
            'prompt_tokens': response['usage']['prompt_tokens'],
            'total_tokens': response['usage']['total_tokens']
        }
        details = old_num_for_model.get('details', [])
        details.append(this_time)
        token_use[model] = {
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'details': details
        }
        with open(path, 'w') as f:
            json.dump(token_use, f, ensure_ascii=False, indent=4)

    def __num_tokens_from_string(self, string: str, encoding_name: str) -> int:
        """Returns the number of tokens in a text string. it seems that openai just check token number as text length"""
        return len(string)
        # encoding = tiktoken.get_encoding(encoding_name)
        # num_tokens = len(encoding.encode(string))
        # return num_tokens

    def __get_model_for_smart(self, messages):
        token_num = self.__num_tokens_from_string(
            json.dumps(messages), "cl100k_base")
        if token_num > 3000:
            model = "gpt-4-32k"
        else:
            model = "gpt-4-0613"
        return model

    def __get_model_for_fast(self, messages):
        token_num = self.__num_tokens_from_string(
            json.dumps(messages), "cl100k_base")
        if token_num > 5000:
            model = "gpt-3.5-turbo-16k-0613"
        else:
            model = "gpt-3.5-turbo-0613"
        return model
    
    