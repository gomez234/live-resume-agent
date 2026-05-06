from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient


SYSTEM_MESSAGE = """
You are a strict evaluator for Samuel Gomez's Live Resume Agent.

Your job is to evaluate whether a draft answer sounds like Samuel speaking naturally.

Check these criteria:
1. First person: uses "I", "my", "me".
2. Conversational: sounds like a real person, not a report.
3. Professional: warm, confident, and polished.
4. Grounded: does not invent unsupported details.
5. Concise: avoids unnecessary headings, long summaries, or robotic structure.

If the answer is good, respond exactly in this format:

APPROVED
FINAL_ANSWER:
<final answer>

If the answer needs improvement, respond exactly in this format:

REVISE
FEEDBACK:
<specific feedback for the answer writer>

Do not include anything else.
"""


def create_tone_evaluator_agent() -> AssistantAgent:
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    return AssistantAgent(
        name="tone_evaluator_agent",
        model_client=model_client,
        system_message=SYSTEM_MESSAGE,
    )