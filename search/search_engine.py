from abc import ABC, abstractmethod
from typing import Generator
from components import SearchResult


class SearchEngine(ABC):

    @abstractmethod
    def search(self, task_id: str, query: str, start_num: int = 0) -> Generator[SearchResult, None, None]:
        """
        do research, return a list of SearchResult. can be empty, but no exception should be raised.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        return the name of the search engine, will be used to identify the search engine.
        will be used to identify the search engine.
        search engine instance with same class MUST return the same name.
        """
        pass
