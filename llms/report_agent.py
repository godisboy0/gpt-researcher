from abc import ABC, abstractmethod
from components import CrawledPage, Summary, FinalReport
from llms.base_llm_util import LLMUtil
from llms.prompt_provider import PromptProvider
from llms.report_outline_generator import ReportOutline, SubTopic
import logging
from utils.cache_manager import cache_result
from utils.time_usage_record import time_usage

logger = logging.getLogger(__name__)


class SummaryGenerator(ABC):

    @abstractmethod
    def generate(self, task_id: str, role_prompt: str, page: CrawledPage, sub_topic: SubTopic) -> Summary:
        pass


def key_gen(*args, **kwargs) -> str:
    page: CrawledPage = kwargs.get("page") if kwargs.get("page") else args[3]
    sub_topic: SubTopic = kwargs.get("sub_topic") if kwargs.get(
        "sub_topic") else args[4]
    return f"{sub_topic.topic}:::{sub_topic.sub_topic}:::{page.url}"


class DefaultSummaryGenerator(SummaryGenerator):

    def __init__(self, prompt_provider: PromptProvider, llm_util: LLMUtil) -> None:
        """
        Args:
            llm_util (LLMUtil): LLMUtil object
            prompt_provider (PromptProvider): PromptProvider object
        """
        self.llm_util = llm_util
        self.prompt_provider = prompt_provider

    @cache_result("summaries", cache_class=Summary, key_gen=key_gen)
    @time_usage
    def generate(self, task_id: str, role_prompt: str, page: CrawledPage, sub_topic: SubTopic) -> Summary:
        logger.info(
            f"generate summary use page {page.url} for sub topic {sub_topic}")
        chunks = self.llm_util.split_for_fast(page.content)
        chunk_dict = {}
        for chunk in chunks:
            prompt = self.prompt_provider.summary_prompt(
                content=chunk, sub_topic=sub_topic)
            chunk_summary = self.llm_util.get_fast_result(messages=[
                {
                    "role": "system",
                    "content": role_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }], task_id=task_id)
            chunk_dict[chunk] = chunk_summary
        if len(chunk_dict) == 1:
            return Summary(sub_topic=sub_topic, page=page, chunks=chunk_dict, summary=list(chunk_dict.values())[0])
        else:
            summary = self.llm_util.get_fast_result(messages=[
                {
                    "role": "system",
                    "content": role_prompt
                },
                {
                    "role": "user",
                    "content": self.prompt_provider.summary_prompt(
                        content="\n\n".join(chunk_dict.values()), sub_topic=sub_topic)
                }], task_id=task_id)
            return Summary(sub_topic=sub_topic, page=page, chunks=chunk_dict, summary=summary)


class ReportAgent(ABC):

    @abstractmethod
    def generate(self, task_id: str, role_prompt: str, summaries: list[Summary], topic: str, outline: ReportOutline) -> FinalReport:
        """
        get report for the page
        """
        pass


class DefaultReportAgent(ReportAgent):

    def __init__(self, prompt_provider: PromptProvider, llm_util: LLMUtil) -> None:
        """
        Args:
            llm_util (LLMUtil): LLMUtil object
            prompt_provider (PromptProvider): PromptProvider object
        """
        self.llm_util = llm_util
        self.prompt_provider = prompt_provider

    @cache_result("final_reports", cache_class=FinalReport, key_gen=lambda *args, **kwargs: kwargs.get("topic") if kwargs.get("topic") else args[4])
    @time_usage
    def generate(self, task_id: str, role_prompt: str, summaries: list[Summary], topic: str, outline: ReportOutline) -> FinalReport:
        logger.info(
            f"call get report for topic {topic} and summaries {summaries}")
        prompt = self.prompt_provider.final_report_prompt(topic=topic,
                                                          outline=outline,
                                                          summary="\n\n".join([summary.summary for summary in summaries]))

        report = self.llm_util.get_smart_result(messages=[
            {
                "role": "system",
                "content": role_prompt
            },
            {
                "role": "user",
                "content": prompt
            }], task_id=task_id)
        logger.debug(f"{topic} has report {report[:100]}")

        return FinalReport(report=report)
