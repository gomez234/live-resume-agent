from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient


SYSTEM_MESSAGE = """
You are a router for Samuel Gomez's Live Resume Agent.

Decide how the user's question should be answered.

Choose RESUME_RAG when:
- The question is about Samuel's experience, projects, skills, education, resume, background, internships, or achievements.

Choose WEB_SEARCH when:
- The question asks about current/public information, companies, technologies, universities, recent news, or external context.

Respond with only one word:
RESUME_RAG
or
WEB_SEARCH
"""


def create_router_agent() -> AssistantAgent:
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    return AssistantAgent(
        name="router_agent",
        model_client=model_client,
        system_message=SYSTEM_MESSAGE,
    )