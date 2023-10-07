from abc import ABC, abstractmethod
from typing import Generator
from components import LLMTokenBill


class LLMUtil(ABC):

    @abstractmethod
    def get_fast_result(self, messages, temperature: int = 0.2, max_tokens: int = None, **kwargs) -> str:
        """
        get the result from the model
        """
        pass

    @abstractmethod
    def get_fast_stream_result(self, messages, temperature: int = 0.2, max_tokens: int = None, **kwargs) -> Generator[str, None, None]:
        """
        get the stream result from the model
        """
        pass

    @abstractmethod
    def get_smart_result(self, messages, temperature: int = 0.2, max_tokens: int = None, **kwargs) -> str:
        """
        get the result from the model
        """
        pass

    @abstractmethod
    def get_smart_stream_result(self, messages, temperature: int = 0.2, max_tokens: int = None, **kwargs) -> Generator[str, None, None]:
        """
        get the stream result from the model
        """
        pass

    @abstractmethod
    def split_for_fast(self, content: str, **kwargs) -> list[str]:
        """
        split the content for fast model
        """
        pass

    @abstractmethod
    def split_for_smart(self, content: str, **kwargs) -> list[str]:
        """
        split the content for smart model
        """
        pass
    
    @abstractmethod
    def get_bill(self, task_id: str) -> LLMTokenBill:
        """
        get the bill from the model
        """
        pass