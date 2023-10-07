from .pipeline import ResearchPipeline
from llms.prompt_provider import DefaultPromptProvider
from llms.role_prompt_generator import DefaultRolePromptGenerator
from llms.report_outline_generator import DefaultOutlineGenerator
from llms.openai_util import DefaultLLMUtil
from llms.question_expander import DefaultQuestionExpander
from llms.report_agent import DefaultSummaryGenerator, DefaultReportAgent
from llms.self_reflection import DefaultSelfReflecter
from search.duckduckgo_engine import DuckDuckGoEngine
from crawlers.crawler_manager import CrawlerManager

def create_pipeline():

    search_engine = DuckDuckGoEngine()
    crawler_manager = CrawlerManager()
    prompt_provider = DefaultPromptProvider()
    llm_util = DefaultLLMUtil()
    role_prompt_generator = DefaultRolePromptGenerator(prompt_provider, llm_util)
    question_expander = DefaultQuestionExpander(prompt_provider, llm_util)
    outline_generator = DefaultOutlineGenerator(prompt_provider, llm_util)
    summary_generator = DefaultSummaryGenerator(prompt_provider, llm_util)
    report_agent = DefaultReportAgent(prompt_provider, llm_util)
    self_reflecter = DefaultSelfReflecter(prompt_provider, llm_util)

    return ResearchPipeline(
        role_prompt_generator=role_prompt_generator,
        question_expander=question_expander,
        search_engine=search_engine,
        crawler_manager=crawler_manager,
        outline_generator=outline_generator,
        report_agent=report_agent,
        summary_generator=summary_generator,
        self_reflecter=self_reflecter
    )