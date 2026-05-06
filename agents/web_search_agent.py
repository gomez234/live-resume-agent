from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.langchain import LangChainToolAdapter

from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool

load_dotenv(override=True)


SYSTEM_MESSAGE = """
You are Samuel Gomez's web research agent.

Your job is to search the internet only when public or current information is needed.

Use web search for:
- current company information
- recent news
- public university or program details
- public context that supports Samuel's answer

Do not use web search for:
- Samuel's private resume details
- questions that should come from Samuel's documents
- personal facts unless they are already public and relevant

After searching, return a short, useful summary/answer.
Do not sound robotic.
"""


def create_web_search_agent() -> AssistantAgent:
    serper = GoogleSerperAPIWrapper()

    langchain_serper = Tool(
        name="internet_search",
        func=serper.run,
        description="Useful for searching the internet for current or public information.",
    )

    autogen_serper = LangChainToolAdapter(langchain_serper)

    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    return AssistantAgent(
        name="web_search_agent",
        model_client=model_client,
        tools=[autogen_serper],
        reflect_on_tool_use=True,
        system_message=SYSTEM_MESSAGE,
    )