from abc import ABC, abstractmethod
import json
from enum import Enum


class CacheAble(ABC):

    @abstractmethod
    def serialize(self) -> dict:
        """
        serialize the object to dict. every element should be json serializable
        """
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, obj: dict) -> "CacheAble":
        """
        deserialize the object from dict
        """
        pass


class RolePrompt(CacheAble):

    def __init__(self, agent: str, agent_role_prompt: str) -> None:
        self.agent = agent
        self.agent_role_prompt = agent_role_prompt

    def serialize(self) -> dict:
        return {
            "agent": self.agent,
            "agent_role_prompt": self.agent_role_prompt
        }

    def deserialize(cls, obj: dict) -> "RolePrompt":
        return RolePrompt(agent=obj["agent"], agent_role_prompt=obj["agent_role_prompt"])

    def __str__(self) -> str:
        return f"agent: {self.agent}, agent_role_prompt: {self.agent_role_prompt}"

    def __repr__(self) -> str:
        return self.__str__()


class SubTopic(CacheAble):
    def __init__(self, topic: str, sub_topic: str, describe: str, word_suggestion: int) -> None:
        self.topic = topic
        self.sub_topic = sub_topic
        self.describe = describe
        self.word_suggestion = word_suggestion

    def serialize(self) -> dict:
        return {
            "topic": self.topic,
            "sub_topic": self.sub_topic,
            "describe": self.describe,
            "word_suggestion": self.word_suggestion
        }

    def deserialize(cls, obj: dict) -> "SubTopic":
        return SubTopic(topic=obj["topic"], sub_topic=obj["sub_topic"], describe=obj["describe"], word_suggestion=obj["word_suggestion"])

    def __str__(self) -> str:
        return f"topic: {self.topic}, sub_topic: {self.sub_topic}, describe: {self.describe}, word_suggestion: {self.word_suggestion}"

    def __repr__(self) -> str:
        return self.__str__()


class ReportOutline(CacheAble):

    def __init__(self, topic: str, top_heading: str, outline_propmt: str, sub_topics: list[SubTopic]) -> None:

        self.topic = topic
        self.top_heading = top_heading
        self.outline_propmt = outline_propmt
        self.sub_topics = sub_topics[:-1]
        self.conclusion = sub_topics[-1]

    def serialize(self) -> dict:
        return {
            "topic": self.topic,
            "top_heading": self.top_heading,
            "outline_propmt": self.outline_propmt,
            "sub_topics": [i.serialize() for i in self.sub_topics],
            "conclusion": self.conclusion.serialize()
        }

    def deserialize(cls, obj: dict) -> "ReportOutline":
        return ReportOutline(topic=obj["topic"],
                             top_heading=obj["top_heading"],
                             outline_propmt=obj["outline_propmt"],
                             sub_topics=[SubTopic.deserialize(SubTopic, i) for i in obj["sub_topics"]] + [SubTopic.deserialize(SubTopic, obj["conclusion"])])

    def __str__(self) -> str:
        return f"topic: {self.topic}, top_heading: {self.top_heading}, outline_propmt: {self.outline_propmt}, sub_topics: {self.sub_topics}, conclusion: {self.conclusion}"

    def __repr__(self) -> str:
        return self.__str__()


class ExpandedQuestion(CacheAble):
    """
    this class is used to store the expanded question. it's just a wrapper of the question and the expanded question.
    but useful if you spilit the question to subquestions.
    """

    def __init__(self, sub_topic: SubTopic, expanded_question: list[str]) -> None:
        self.sub_topic = sub_topic
        self.expanded_question = expanded_question

    def serialize(self) -> dict:
        return {
            "sub_topic": self.sub_topic.serialize(),
            "expanded_question": self.expanded_question
        }

    def deserialize(cls, obj: dict) -> "ExpandedQuestion":
        return ExpandedQuestion(sub_topic=SubTopic.deserialize(SubTopic, obj["sub_topic"]), expanded_question=obj["expanded_question"])

    def __str__(self) -> str:
        return f"sub_topic: {self.sub_topic}, expanded_question: {self.expanded_question}"

    def __repr__(self) -> str:
        return self.__str__()


class SearchResult(CacheAble):

    def __init__(self, url: str, title: str, abstract: str, question: str = None):
        self.url = url
        self.title = title
        self.abstract = abstract
        self.question = question

    def serialize(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "abstract": self.abstract,
            "question": self.question
        }

    def deserialize(cls, obj: dict) -> "SearchResult":
        return SearchResult(url=obj["url"], title=obj["title"], abstract=obj["abstract"], question=obj["question"])

    def __str__(self) -> str:
        return f"SearchResult(url={self.url}, title={self.title}, abstract={self.abstract} question={self.question})"

    def __repr__(self) -> str:
        return self.__str__()


class CrawledPage(CacheAble):

    def __init__(self, url: str, title: str, content: str):
        self.url = url
        self.title = title
        self.content = content

    def serialize(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content
        }

    def deserialize(cls, obj: dict) -> "CrawledPage":
        return CrawledPage(url=obj["url"], title=obj["title"], content=obj["content"])

    def __str__(self):
        return f"url: {self.url}, title: {self.title}, content_len: {len(self.content)}, content: {self.content[:100]}"

    def __repr__(self):
        return self.__str__()


class Summary(CacheAble):

    def __init__(self, sub_topic: SubTopic, page: CrawledPage, chunks: dict[str, str], summary: str) -> None:
        """
        Args:
            topic_list (list[str]): the topic_chain
            page (CrawledPage): the raw page 
            chunks (dict[str, str]): the chunks that contains the summary, key is the chunk content, value is the summary
            summary (str): the summary for the page
        """
        self.sub_topic = sub_topic
        self.page = page
        self.chunks = chunks
        self.summary = summary

    def serialize(self) -> dict:
        return {
            "sub_topic": self.sub_topic.serialize(),
            "page": self.page.serialize(),
            "chunks": {k: v for k, v in self.chunks.items()},
            "summary": self.summary
        }

    def deserialize(cls, obj: dict) -> "Summary":
        return Summary(sub_topic=SubTopic.deserialize(SubTopic, obj["sub_topic"]),
                       page=CrawledPage.deserialize(CrawledPage, obj["page"]),
                       chunks={k: v for k, v in obj["chunks"].items()},
                       summary=obj["summary"])

    def __str__(self) -> str:
        return f"sub_topic: {self.sub_topic}, page: {self.page}, chunks_size: {len(self.chunks)}, summary: {self.summary[:100]}"

    def __repr__(self) -> str:
        return self.__str__()


class DeterminResult(CacheAble):

    def __init__(self, content: str, relavance: bool) -> None:
        self.content = content
        self.relavance = relavance

    def serialize(self) -> dict:
        return {
            "content": self.content,
            "relavance": self.relavance
        }

    def deserialize(cls, obj: dict) -> "DeterminResult":
        return DeterminResult(content=obj["content"], relavance=obj["relavance"])

    def __str__(self) -> str:
        return f"content: {self.content[:100]}, relavance: {self.relavance}"

    def __repr__(self) -> str:
        return self.__str__()


class FinalReport(CacheAble):

    def __init__(self, report: str) -> None:
        """
        Args:
            report (str): the report
        """
        self.report = report

    def serialize(self) -> dict:
        return {
            "report": self.report
        }

    def deserialize(cls, obj: dict) -> "FinalReport":
        return FinalReport(report=obj["report"])

    def __str__(self) -> str:
        return f"report: {self.report[:100]}"

    def __repr__(self) -> str:
        return self.__str__()


class TokenType(Enum):
    Prompt = "输入的prompt的token"
    Completion = "llm输出的token"


class TokenUsage(CacheAble):

    def __init__(self, model: str, token_type: TokenType, used: int, bill: float = None) -> None:
        """
        Args:
            model (str): the model
            token_type (TokenType): the token type
            used (int): the used
        """
        self.model = model
        self.token_type = token_type
        self.used = used
        self.bill = bill

    def set_bill(self, bill: float) -> None:
        """
        Args:
            bill (float): the bill
        """
        self.bill = bill

    def serialize(self) -> dict:
        return {
            "model": self.model,
            "token_type": self.token_type.name,
            "used": self.used,
            "bill": self.bill
        }
    
    def deserialize(cls, obj: dict) -> "TokenUsage":
        return TokenUsage(model=obj["model"], token_type=TokenType[obj["token_type"]], used=obj["used"], bill=obj.get("bill", None))
    
    def __str__(self) -> str:
        return f"model: {self.model}, token_type: {self.token_type}, used: {self.used}, bill: {self.bill}"
    
    def __repr__(self) -> str:
        return self.__str__()
    

class TokenPrice(CacheAble):

    def __init__(self, model: str, token_type: TokenType, price: float) -> None:
        """
        Args:
            model: the model
            token_type: the token type
            price (float): the price, in dollar, here should be the price of 1000 token price 
        """
        self.model = model
        self.token_type = token_type
        self.price = price
    
    def serialize(self) -> dict:
        return {
            "model": self.model,
            "token_type": self.token_type.name,
            "price": self.price
        }
    
    def deserialize(cls, obj: dict) -> "TokenPrice":
        return TokenPrice(model=obj["model"], token_type=TokenType[obj["token_type"]], price=obj["price"])
    
    def __str__(self) -> str:
        return f"model: {self.model}, token_type: {self.token_type}, price: {self.price}"
    
    def __repr__(self) -> str:
        return self.__str__()


class LLMTokenBill(CacheAble):

    def __init__(self, usage: list[TokenUsage], price: list[TokenPrice], total_bill: float = None) -> None:
        """
        Args:
            usage (list[TokenUsage]): the token usage
            price (list[TokenPrice]): the token price
            total_bill (float): the total bill
        """
        self.usage = usage
        self.price = price
        self.total_bill = total_bill
        self.__calculate_bill()

    def __calculate_bill(self) -> None:
        price: dict[str, float] = {x.model + x.token_type.name: x.price for x in self.price}
        usage: dict[str, int] = {x.model + x.token_type.name: x.used for x in self.usage}
        for key in usage.keys():
            if key not in price:
                price[key] = 0
        for u in self.usage:
            u.set_bill(price[u.model + u.token_type.name] * u.used / 1000)
        self.total_bill = sum([price[key] * usage[key] for key in usage.keys()]) / 1000

    def serialize(self) -> dict:
        return {
            "usage": [i.serialize() for i in self.usage],
            "price": [i.serialize() for i in self.price],
            "total_bill": self.total_bill
        }

    def deserialize(cls, obj: dict) -> "LLMTokenBill":
        return LLMTokenBill(usage=[TokenUsage.deserialize(TokenUsage, i) for i in obj["usage"]], 
                            price=[TokenPrice.deserialize(TokenPrice, i) for i in obj["price"]],
                            total_bill=obj["total_bill"])

    def __str__(self) -> str:
        return f"usage: {self.usage}, price: {self.price}, total_bill: {self.total_bill}"

    def __repr__(self) -> str:
        return self.__str__()


if __name__=="__main__":
    print(TokenType.Prompt.name)
    print(TokenType["Prompt"])