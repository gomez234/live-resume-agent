"""
This file defines a simple program that creates an agent for evaluating the tone of answers
provided by a user, specifically for Samuel Gomez's Live Resume Agent. 

The overall purpose is to set up an agent that assesses whether the draft answers sound natural 
and meet specific criteria. The flow includes importing necessary classes, defining a system 
message that guides the evaluation, and creating a function that returns an instance of the 
tone evaluation agent with the appropriate configurations.

The file expects no direct input from a user in its execution, and it outputs an instance of 
the AssistantAgent class that contains the logic to evaluate answers based on the defined criteria. 
This agent can then be used in other parts of the program where the evaluation needs to take place.
"""

# Import the necessary libraries
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Define a constant string named SYSTEM_MESSAGE, which outlines the evaluation criteria 
# for the agent. This message will guide the agent in its evaluation tasks.
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

# Define a function named create_tone_evaluator_agent that returns an AssistantAgent instance.
def create_tone_evaluator_agent() -> AssistantAgent:
    # Create an instance of the OpenAIChatCompletionClient with a specified model "gpt-4o-mini".
    # This client will be responsible for generating responses or evaluations using the AI model.
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    # Return an instance of the AssistantAgent configured with a name, a model client,
    # and the system message for evaluation criteria defined earlier.
    return AssistantAgent(
        name="tone_evaluator_agent", # Assign the name for this agent instance.
        model_client=model_client, # Pass the instantiated model client to the agent.
        system_message=SYSTEM_MESSAGE, # Provide the system message for the evaluation.
    )