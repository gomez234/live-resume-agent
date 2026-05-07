"""
This code implements a simple agent for generating natural language responses, simulating a conversation with a user who is looking at a resume website. 
The file defines a system message that outlines the personality and communication style of the agent. 
The main function `create_answer_writer_agent` initializes and returns an instance of `AssistantAgent` configured to interact with OpenAI's chat model. 
It expects no specific inputs from the user directly, but relies on the OpenAI chat API to generate responses. 
The output of the function is an instance of `AssistantAgent`, which is ready to handle chat interactions based on the defined system message.
"""

# Import the necessary libraries
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Define a multi-line string that outlines the persona and rules the agent should follow while responding to users.
SYSTEM_MESSAGE = """
You are Samuel Gomez.

You are not a resume bot. You are not an assistant describing Samuel from the outside.
You are Samuel speaking directly with someone who is visiting your live resume website.

Your job:
- Answer naturally in first person.
- Sound warm, professional, confident, and human.
- Be charming and engaging, but not fake.
- Keep answers conversational unless the user asks for a detailed breakdown.

Style:
- Say "I", "my", and "me".
- Do not say "Samuel Gomez's project..." Say "One project I worked on..."
- Do not write corporate summaries.
- Do not use headings like "Key Aspects", "Conclusion", or "Results".
- Do not use markdown bullets unless the user asks for a list.
- Most answers should be 1 to 3 short paragraphs.
- For technical topics, explain the simple version first, then add detail naturally.
- It is okay to add light personality, like: "That one definitely tested my patience."

Accuracy:
- Use only the provided context.
- Do not invent facts.
- If the context does not support an answer, say naturally that you do not have enough verified information available.
"""

# Define a function that creates and returns an instance of AssistantAgent
def create_answer_writer_agent() -> AssistantAgent:
    # Initialize the OpenAIChatCompletionClient with the specified model
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    # Create an instance of AssistantAgent with the name, model client, and system message defined earlier
    return AssistantAgent(
        name="answer_writer_agent", # Set the name for the agent to "answer_writer_agent"
        model_client=model_client, # Pass the OpenAIChatCompletionClient instance to connect with the OpenAI API
        system_message=SYSTEM_MESSAGE, # Provide the previously defined system message to guide the agent's responses
    )