from abc import ABC, abstractmethod
from components import SubTopic, ReportOutline
import time


class PromptProvider(ABC):

    @abstractmethod
    def auto_agent_prompt(self) -> str:
        """
        use to generate system prompt for the specific agent type.
        see DefaultPromptProvider.get_auto_agent_generation_instructions for an example
        """
        pass

    @abstractmethod
    def search_queries_prompt(self, sub_topic: SubTopic) -> str:
        """
        use to expand the search queries for the sub_topics.

        Args:
            sub_topic (SubTopic): sub topic of the topic user asked
        """
        pass

    @abstractmethod
    def outline_prompt(self, topic: str) -> str:
        """
        use to generate the outline of the report

        Args:
            task_id (str): the task id, some implementations may use it, to say... request the user to write the outline
            topic (str): the topic
            research_type (str): the research type
        """
        pass

    @abstractmethod
    def self_reflection_prompt(self, sub_topic: SubTopic, content: str) -> str:
        """
        use to generate the self reflection prompt for the giving sub topic.

        Args:
            role_prompt (str): the role prompt
            sub_topic (SubTopic): the sub topic

        Returns:
            str: the self reflection prompt
        """
        pass

    @abstractmethod
    def summary_prompt(self, content: str, sub_topic: SubTopic) -> str:
        """
        use to generate the summary prompt for the giving sub topic.

        Args:
            content (str): the content
            sub_topic (SubTopic): the sub topic

        Returns:
            str: the summary prompt
        """
        pass

    @abstractmethod
    def final_report_prompt(self, topic: str, outline: ReportOutline, summary: str) -> str:
        """
        use to generate the final report prompt for the giving sub topic.

        Returns:
            str: the final report prompt
        """
        pass

class DefaultPromptProvider(PromptProvider):

    def auto_agent_prompt(self) -> str:
        return """This task involves researching a given topic, regardless of its complexity or the availability of a definitive answer. The research is conducted by a specific agent, defined by its type and role, with each agent requiring distinct instructions.
Agent
The agent is determined by the field of the topic and the specific name of the agent that could be utilized to research the topic provided. Agents are categorized by their area of expertise, and each agent type is associated with a corresponding emoji.
YOU SHOULD ALWAYS ANSWER IN THE LANGUAGE OF THE USER'S QUESTION.

examples:
task: "should I invest in apple stocks?"
response: 
{
    "agent": "💰 Finance Agent",
    "agent_role_prompt": "You are a seasoned finance analyst AI assistant. Your primary goal is to compose comprehensive, astute, impartial, and methodically arranged financial reports based on provided data and trends."
}
task: "could reselling sneakers become profitable?"
response: 
{ 
    "agent":  "📈 Business Analyst Agent",
    "agent_role_prompt": "You are an experienced AI business analyst assistant. Your main objective is to produce comprehensive, insightful, impartial, and systematically structured business reports based on provided business data, market trends, and strategic analysis."
}
task: "what are the most interesting sites in Tel Aviv?"
response:
{
    "agent":  "🌍 Travel Agent",
    "agent_role_prompt": "You are a world-travelled AI tour guide assistant. Your main purpose is to draft engaging, insightful, unbiased, and well-structured travel reports on given locations, including history, attractions, and cultural insights."
}
AGAIN, YOU SHOULD ALWAYS ANSWER IN THE LANGUAGE OF THE USER'S QUESTION.
    """

    def search_queries_prompt(self, sub_topic: SubTopic) -> str:
        return f'here is a task, about generating a research report for the following topic: "{sub_topic.topic}"'\
            "we decided to break the topic into several sub topics, and finish seperately, "\
            f'the sub topic we need to finish is: "{sub_topic.sub_topic}", it aims to help us finish this part of the report: "{sub_topic.describe}"'\
            f'here you need to write 1-2 google search queries for us, these search queries should be able to help us to finish this sub topic'\
            f"and these queries should be different from each other, "\
            'You must respond with a list of strings in the following format: ["query 1", "query 2"], '\
            "AND YOU SHOULD ALWAYS ANSWER IN THE LANGUAGE OF THE USER'S TOPIC."

    def outline_prompt(self, topic: str) -> str:
        return "This task involves using serveral pieces of information to generate a research report about a given topic using Large Language Model such as GPT.\n"\
            "you should give a prompt to instruct the model to generate the report. this prompt will detailing the task, specify section headings,"\
            "provide a clear step by step instructions for the model, and give the suggests length for each section.\n'\
            'the prompt should be at least 100 tokens long, MUST USE well-formed MARKDOWN syntax to mark the headings, "\
            "The first-level heading should be the topic itself, generate up to second-level headings, NO sub-levels should be generated.\n"\
            "AND ALWAYS GENERATE IN THE LANGUAGE OF THE TOPIC.\n"\
            f'the topic is """{topic}"""\n'\
            "here is one example of the report generated by the model, starts and ends with ```:"\
            """
```# How is the movie 'The Wandering Earth 2'?

To generate a comprehensive research report on the movie 'The Wandering Earth 2', please follow the instructions below:

## Introduction--200words
    - Begin with a brief introduction about the movie. Include details such as the director, release date, and the main cast. Also, provide a short synopsis of the movie without giving away any spoilers.

## Plot Summary--500words
    - Provide a detailed summary of the plot. Remember to warn readers about potential spoilers in this section.

## Critical Reception--1000words
    - Analyze the critical reception of the movie. Include information about the ratings and reviews it received from major film critics and review aggregators like Rotten Tomatoes and IMDb.

## Box Office Performance--200words
    - Discuss the movie's performance at the box office. Include details about its budget and its earnings globally and in different markets.

## Audience Reception--1000words
    - Discuss how the movie was received by the audience. Include information about audience ratings and reviews from platforms like IMDb and Rotten Tomatoes.

## Technical Aspects--800words
    - Discuss the technical aspects of the movie such as the cinematography, sound design, visual effects, and editing. Include information about any awards or nominations the movie received for these aspects.

## Conclusion--200words
    - Summarize the main points discussed in the report. Provide a balanced conclusion about the overall quality and success of the movie.```"""

    def self_reflection_prompt(self, sub_topic: SubTopic, content: str) -> str:
        content = content.replace('"""', '"')
        content = content.replace('""', '"')
        return f'here is a task, about generating a research report for the following topic: "{sub_topic.topic}"'\
            f'we have outlined the report, and obtained some materials for one of these headings, which is: "{sub_topic.sub_topic}", '\
            f'it aims to help us finish this part of the report: "{sub_topic.describe}". '\
            f'here is the material we obtained: """{content}"""'\
            f'now you should determine if this material is sufiicient, or at least helpful to finish this part of the report.'\
            f'particularly, if this topic could be a current affairs issue, you should determine if this material is outdated, and today is "{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}",'\
            ' any outdated matrial is irrelevant with the issue.'\
            f'reply with "YES" or "NO". NO MORE WORDS ARE ALLOWED.'
    
    def summary_prompt(self, content: str, sub_topic: SubTopic) -> str:
        content = content.replace('"""', '"')
        content = content.replace('""', '"')
        return f'here is a task, about generating a research report for the following topic: "{sub_topic.topic}"'\
            f'we have outlined the report, and obtained some materials for one of these headings, which is: "{sub_topic.sub_topic}", '\
            f'it aims to help us finish this part of the report: "{sub_topic.describe}". '\
            f'you should summarize the material in depth. Include all factual information, numbers, stats etc if available.'\
            f'here is the material we obtained: """{content}"""'
    
    def final_report_prompt(self, topic: str, outline: ReportOutline, summary: str) -> str:
        summary = summary.replace('"""', '"')
        summary = summary.replace('""', '"')
        sub_topics = "\n".join([f"- {i.sub_topic}: {i.describe}" for i in outline.sub_topics])
        return f'here is a task, about generating a research report for the following topic: "{topic}"'\
            f'here is some materials we obtained: """{summary}"""'\
            f'you should generate the report focusing on the following topics: """{sub_topics}"""'\
            f'remember to remove all inrelevant, repeated, or contradictory content.'\
            'make sure the report is well structured, informative, in depth, with facts and numbers if available.'