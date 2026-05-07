"""
This file implements a simple agent router for a project called Samuel Gomez's Live Resume Agent. 
The router helps determine the appropriate way to respond to user questions related to Samuel’s experiences and current information. 

The file works by defining a constant `SYSTEM_MESSAGE` that provides instructions on how to classify questions. 
It then defines a function `create_router_agent` that initializes an instance of an `AssistantAgent` with specific parameters. 

The expected input for this code is the question posed by a user, which the agent will receive through its implementation. 
The output is an instance of `AssistantAgent`, configured to route queries based on the pre-defined logic in `SYSTEM_MESSAGE`, resulting in either a "RESUME_RAG" or "WEB_SEARCH" classification.
"""

# Import the necessary libraries
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Defining a constant string that contains the system message for the agent
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

# Defining a function named create_router_agent that returns an AssistantAgent instance
def create_router_agent() -> AssistantAgent:
    # Creating an instance of OpenAIChatCompletionClient with the specified model 'gpt-4o-mini'
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    # Returning a new instance of AssistantAgent with the name, model client, and system message provided
    return AssistantAgent(
        name="router_agent", # Assigning a name to the agent for identification
        model_client=model_client, # Connecting the agent to the OpenAI model client
        system_message=SYSTEM_MESSAGE, # Providing the agent with the rules to classify user queries
    )