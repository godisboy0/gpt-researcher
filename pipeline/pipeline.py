from llms.role_prompt_generator import RolePromptGenerator
from llms.question_expander import QuestionExpander
from search.search_engine import SearchEngine
from crawlers.crawler_manager import CrawlerManager
from llms.report_agent import ReportAgent, SummaryGenerator
from llms.report_outline_generator import ReportOutlineGenerator
from llms.self_reflection import SelfReflecter
from components import CrawledPage, Summary, SubTopic, SearchResult, RolePrompt
import logging
import os
import time
from markdown2 import markdown_path
from weasyprint import HTML, CSS
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

def generate_task_id(input_str: str) -> str:
    return ''.join([x if x.isalnum() else '_' for x in input_str])


class ResearchPipeline:

    def __init__(self, role_prompt_generator: RolePromptGenerator,  question_expander: QuestionExpander,
                 search_engine: SearchEngine, crawler_manager: CrawlerManager, report_agent: ReportAgent,
                 outline_generator: ReportOutlineGenerator, self_reflecter: SelfReflecter,
                 summary_generator: SummaryGenerator):
        self.role_prompt_generator = role_prompt_generator
        self.question_expander = question_expander
        self.search_engine = search_engine
        self.crawler_manager = crawler_manager
        self.report_agent = report_agent
        self.summary_generator = summary_generator
        self.outline_generator = outline_generator
        self.self_reflecter = self_reflecter

    def do_research(self, topic: str) -> str:
        start_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        task_id = generate_task_id(topic)

        agent_prompt = self.role_prompt_generator.generate(task_id, topic)
        logger.info(f"agent prompt: {agent_prompt}")

        outline = self.outline_generator.generate(task_id,
                                                  agent_prompt.agent_role_prompt, topic)
        logger.info(f"outline: {outline}")

        sub_topics = outline.sub_topics

        # crawl really token a long time, lets do it in parallel
        need_relavance_page_num_for_each_query = 2
        sub_topic_and_query = []
        for sub_topic in sub_topics:
            logger.info(f"doing research for sub topic: {sub_topic}")
            queriers = self.question_expander.expand(task_id,
                                                     agent_prompt.agent_role_prompt, sub_topic)
            sub_topic_and_query.extend([(sub_topic, q)
                                       for q in queriers.expanded_question])

        parllel_level = len(sub_topic_and_query)
        executor = ThreadPoolExecutor(max_workers=parllel_level)
        futures = []
        summaries = []
        for sub_topic, query in sub_topic_and_query:
            futures.append(executor.submit(self.summary_for_sub_topic, task_id,
                           agent_prompt, sub_topic, query, need_relavance_page_num_for_each_query))

        for future in as_completed(futures):
            try:
                summary = future.result()
                summaries.append(summary)
            except Exception as e:
                logger.exception(f"error when batch_crawl: {e}")
                continue

        final_report = self.report_agent.generate(task_id,
                                                  agent_prompt.agent_role_prompt, summaries, topic, outline)
        end_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        logger.info(f'task {task_id} done, start at {start_time}, end at {end_time}')
        
        self.persist_report(task_id, final_report.report)

    def summary_for_sub_topic(self, task_id: str, agent_prompt: RolePrompt, sub_topic: SubTopic, query: str, need_relavance_page_num_for_each_query: int) -> Summary:
        """
        for each query(at most two) for each sub topic, we do a summary. we do it as following:
            1. search for the query;
            2. crawl the pages one by one;
            3. do summary for the pages, determine if the page is relavant to the sub topic;
            4. repeat until we have enough relavant pages, which is need_relavance_page_num_for_each_query;
        """
        logger.info(f"doing summary for query: {query}")

        search_results = self.search_engine.search(task_id, query, 0)
        single_summaries: list[Summary] = []
        for search_result in search_results:
            try:
                logger.info(f"doing crawl for url: {search_result.url}")
                page = self.crawler_manager.crawl(task_id, search_result.url)
                if page is None:
                    logger.warning(
                        f"crawl failed for url: {search_result.url}")
                    continue
                logger.info(
                    f"crawl success for url: {search_result.url}, page: {page}")
                summary = self.summary_generator.generate(
                    task_id, agent_prompt.agent_role_prompt, page, sub_topic)
                logger.info(f"summary: {summary}")
                page_relevance = self.self_reflecter.determin_relavance(
                    task_id, agent_prompt.agent_role_prompt, sub_topic, summary.summary)
                if page_relevance.relavance:
                    single_summaries.append(summary)
                    if len(single_summaries) >= need_relavance_page_num_for_each_query:
                        return self.summary_generator.generate(task_id, agent_prompt.agent_role_prompt,
                                                               CrawledPage(
                                                                   url=f"summary:{sub_topic.sub_topic}:::{query}",
                                                                   title=f"summary:{sub_topic.sub_topic}:::{query}",
                                                                   content="\n\n".join(
                                                                       [s.summary for s in single_summaries]),
                                                               ),
                                                               sub_topic)
                    logger.info(
                        f"page {search_result.url} is relavant to sub topic {sub_topic}")
                else:
                    logger.info(
                        f"page {search_result.url} is not relavant to sub topic {sub_topic}")
            except Exception as e:
                logger.exception(f"error when batch_crawl: {e}")
                continue

    def persist_report(self, task_id: str, final_report: str) -> None:
        logging.getLogger("markdown").setLevel(logging.WARNING)
        logging.getLogger('weasyprint').setLevel(logging.WARNING)
        logging.getLogger('fontTools').setLevel(logging.WARNING)
        base_dir = os.path.join(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "output"), task_id)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        md_file = os.path.join(base_dir, "report.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(final_report)
        html = markdown_path(md_file)
        css = CSS(string='''
            @page {
                size: A4 portrait;
                margin: 1cm;
            }
            ''')
        pdf_file = os.path.join(base_dir, "report.pdf")
        HTML(string=html).write_pdf(pdf_file, stylesheets=[css])
