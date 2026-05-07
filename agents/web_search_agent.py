"""
This Python file is designed to create and configure a web search agent using various libraries and tools. 
It leverages the OpenAI API for completing chat-based tasks and the Google Search API to fetch current information. 
The overall flow involves loading environment variables, defining the agent's behavior through a system message, 
and creating a function that initializes and returns the configured agent. 
The expected inputs are the environment variables that provide API keys or configuration settings. 
The output is an instance of the AssistantAgent, which is ready to perform web searches and provide useful summaries to a user.
"""

# Import the necessary libraries
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.langchain import LangChainToolAdapter
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool

# Load environment variables from a .env file, if present, and override existing variables if they are defined
load_dotenv(override=True)

# Define a string constant called SYSTEM_MESSAGE that describes the parameters and behavior 
# of the agent being created, including guidelines for when to use web searches and what type of information to avoid
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

# Define a function called create_web_search_agent that returns an instance of AssistantAgent
# The function does not take any input parameters and explicitly returns an AssistantAgent object
def create_web_search_agent() -> AssistantAgent:
    # Create an instance of GoogleSerperAPIWrapper, which will be used to perform internet searches
    serper = GoogleSerperAPIWrapper()
    # Create an instance of Tool with a specific function for searching the internet
    langchain_serper = Tool(
        name="internet_search", # Assign a name to the tool for identification
        func=serper.run, # Specify the function to call when using this tool, here it will call the run method of serper
        description="Useful for searching the internet for current or public information.", # Provide a brief description of the tool's purpose
    )
    # Adapt the langchain_serper tool to be used with the LangChain framework
    autogen_serper = LangChainToolAdapter(langchain_serper)
    # Create an instance of OpenAIChatCompletionClient, specifying the model to use for text generation
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    # Return an instance of AssistantAgent, which is configured with the specified name, model client, tools, reflection behavior, and system message
    return AssistantAgent(
        name="web_search_agent", # Set a name for this agent
        model_client=model_client, # Provide the model client to the agent for processing requests
        tools=[autogen_serper], # List of tools that the agent can use, in this case, only autogen_serper
        reflect_on_tool_use=True, # Enable reflection on tool use, which helps the agent improve over time
        system_message=SYSTEM_MESSAGE, # Pass the system message that defines the agent's behavior and guidelines
    )