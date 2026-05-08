"""
This Python file is designed to create an escalation agent for a live resume application. 
The purpose of the escalation agent is to determine when user questions should be escalated to Samuel Gomez. 
The file outlines a clear set of criteria and rules for escalation based on user inquiries. 
The expected input is a user question directed towards the system, and the outputs are either a decision to escalate or not, formatted in a specific response structure. 
"""

# Import the necessary libraries
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# System message that defines the role and responsibilities of the escalation agent
# It includes detailed guidelines on when to escalate user questions to Samuel Gomez.
SYSTEM_MESSAGE = """
You are the escalation agent for Samuel Gomez's Live Resume Agent.

Your job is to decide if a user question should be escalated to Samuel directly.

Escalate when:
- The available context does not contain enough verified information.
- The question asks for private or sensitive information (information from Samuel's personal life specifically).
- The question asks for Samuel's direct opinion, availability, phone number, address, salary, immigration details, family, relationships, or anything personal that should not be guessed.
- The draft answer says it does not know or is uncertain.
- Answering would require inventing facts.

Do not escalate when:
- The answer is clearly supported by Samuel's documents or web search results.
- The question can be answered safely from the available context.

Respond only in this format:

NO_ESCALATION

or

ESCALATE
REASON:
<short reason>
MESSAGE_TO_USER:
<natural first-person message as Samuel telling the user that I should answer directly>
"""
# Function that creates and returns an escalation agent instance
def create_escalation_agent() -> AssistantAgent:
    # Creating an instance of OpenAIChatCompletionClient using the "gpt-4o-mini" model 
    # This client will be responsible for generating responses based on user queries.
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    return AssistantAgent(
        name="escalation_agent", # Assign the name for this agent instance.
        model_client=model_client, # Pass the instantiated model client to the agent.
        system_message=SYSTEM_MESSAGE, # Provide the system message for the evaluation.
    )