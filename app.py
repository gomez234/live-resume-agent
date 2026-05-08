"""
This Python file is designed to facilitate a chat interface where users can interact with a virtual assistant named Samuel Gomez. 
It integrates multiple agents to handle user messages, perform web searches, generate answers, and evaluate responses. 
The file expects a user message (text) and a message history (list of previous exchanges). 
As output, it produces a final response to the user's question, looking to be conversational, warm, and informative, 
while also handling feedback validation through evaluation of the generated answers.
"""

# Import the necessary libraries for the functionality of the chat application.
import asyncio
from dotenv import load_dotenv
import gradio as gr
from autogen_agentchat.messages import TextMessage
import re

# Importing various agent creation functions for different roles in the chat application.
from agents.answer_writer_agent import create_answer_writer_agent
from agents.evaluator_agent import create_tone_evaluator_agent
from agents.router_agent import create_router_agent
from agents.web_search_agent import create_web_search_agent
from agents.escalation_agent import create_escalation_agent

# Importing the functions from specified modules.
from tools.retriever import retrieve_context
from tools.escalation_tools import handle_escalation_submission

# Load the environment variables from a .env file, allowing configuration without hardcoding sensitive information.
# The override=True option allows existing variables to be overridden by values in the .env file.
load_dotenv(override=True)

# Instantiating various agents using the respective creation functions.
router_agent = create_router_agent()
web_search_agent = create_web_search_agent()
answer_writer_agent = create_answer_writer_agent()
evaluator_agent = create_tone_evaluator_agent()
escalation_agent = create_escalation_agent()

# A helper function to check if a given string appears to be an email address.
def looks_like_email(text: str) -> bool:
    # Uses regex to validate email format.
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", text.strip()) is not None

# Dictionary to track pending escalations, holding information about active escalations and relevant questions and reasons.   
pending_escalation = {
    "active": False,
    "question": None,
    "reason": None,
}

# Asynchronous function to handle chat interactions with users.
async def chat_async(message, history):
    # Use the global pending_escalation variable to track state across function calls.
    global pending_escalation
    # Check if there is an active escalation that needs to be processed first.
    if pending_escalation["active"]:
        # Check if the incoming message looks like an email address.
        if looks_like_email(message):
            # Store the trimmed input email address for processing.
            user_email = message.strip()
            # Handle the submission for escalation, including the user's email and relevant question.
            handle_escalation_submission(
                question=pending_escalation["question"],
                user_email=user_email,
                reason=pending_escalation["reason"],
            )
            # Reset pending escalation state after handling it.
            pending_escalation = {
                "active": False,
                "question": None,
                "reason": None,
            }
            # Return a confirmation response to the user about the receipt of their email.
            return "Perfect — thanks for sharing your email. I’ll make sure Samuel sees your question and can follow up directly."
        # If the message does not look like an email, prompt the user for a valid email address.
        return "That looks like something other than an email. Could you please send the best email address for Samuel to follow up?"
    # Route the incoming message using the router agent and wait for a response asynchronously.
    router_response = await router_agent.on_messages(
        [TextMessage(content=message, source="user")], # Send user message wrapped in a TextMessage object.
        cancellation_token=None,  # No cancellation token needed for this operation.
    )
    # Process the response from the router agent to determine the next action.
    route = router_response.chat_message.content.replace("TERMINATE", "").strip()
    # Check if the routed decision is to perform a web search.
    if route == "WEB_SEARCH":
        # Perform a web search for the user's message and await the response.
        web_response = await web_search_agent.on_messages(
            [TextMessage(content=message, source="user")], # Send user message again for context.
            cancellation_token=None, # No cancellation token needed.
        )
        # Store the trimmed context from the web search.
        relevant_context = web_response.chat_message.content.replace("TERMINATE", "").strip()
    else:
        # Retrieve context based on the user's message if web search is not necessary.
        relevant_context = retrieve_context(message)
     # Prepare a prompt for the escalation agent to determine if the query needs to go up to Samuel.
    escalation_prompt = f"""
User question:
{message}

Available context:
{relevant_context}

Should this question be escalated to Samuel directly?
"""
    # Call the escalation agent with the prepared escalation prompt and wait for its decision.
    escalation_response = await escalation_agent.on_messages(
        [TextMessage(content=escalation_prompt, source="user")], # Send the prompt to the escalation agent.
        cancellation_token=None, # No cancellation token needed.
    )
    # Process the escalation agent's response regarding whether to escalate the query.
    escalation_decision = escalation_response.chat_message.content.replace("TERMINATE", "").strip()
     # Determine if the agent has decided to escalate the query.
    if escalation_decision.startswith("ESCALATE"):
        # Initialize a variable to hold the escalation reason.
        reason = ""
        # Check for the presence of a reason and a message in the escalation response.
        if "REASON:" in escalation_decision and "MESSAGE_TO_USER:" in escalation_decision:
            reason = escalation_decision.split("REASON:", 1)[-1].split("MESSAGE_TO_USER:", 1)[0].strip()
        # Update the global pending escalation state, indicating it is now active.
        pending_escalation = {
            "active": True, # Mark escalation as active.
            "question": message, # Store the user's query as the escalation question.
            "reason": reason, # Store the reason for the escalation.
        }
        # Extract any user message provided in the escalation decision to inform the user.
        if "MESSAGE_TO_USER:" in escalation_decision:
            # Capture the user message and trim it.
            message_to_user = escalation_decision.split("MESSAGE_TO_USER:", 1)[-1].strip()
        else:
            # Default message if none is provided.
            message_to_user = "I don’t have enough verified information to answer that confidently."
        # Return the extracted message along with a prompt for the user to provide their email.
        return f"{message_to_user}\n\nWhat’s the best email where Samuel can follow up with you?"
    # Initialize feedback and draft content variables for generating a response.
    # Holds any feedback received on drafts generated.
    feedback = ""
    # Holds the content of the drafts generated by the answer writing agent.
    draft_content = ""
    # Attempt to generate an appropriate answer up to three times, allowing for evaluation and revision.
    for attempt in range(3):
        writer_prompt = f"""
Context:
{relevant_context}

User question:
{message}

Previous feedback, if any:
{feedback}

Write the best possible answer as Samuel.

Important:
- Speak in first person.
- Be conversational, warm, professional, and natural.
- Do not sound like a resume bot.
- Do not use headings unless the user asks for structure.
- Do not invent unsupported details.
"""
        # Call the answer writer agent with the prepared prompt and wait for the generated draft response.
        draft_response = await answer_writer_agent.on_messages(
            [TextMessage(content=writer_prompt, source="user")], # Send the prompt in a TextMessage object.
            cancellation_token=None, # No cancellation token needed.
        )
        # Trim and store the drafted response from the agent.
        draft_content = draft_response.chat_message.content.replace("TERMINATE", "").strip()
        # Prepare a prompt for the evaluator agent to assess the quality of the draft response.
        evaluator_prompt = f"""
User question:
{message}

Context:
{relevant_context}

Draft answer:
{draft_content}

Evaluate the answer.
"""
        # Call the evaluator agent with the evaluation prompt and wait for its decision.
        evaluation_response = await evaluator_agent.on_messages(
            [TextMessage(content=evaluator_prompt, source="user")],  # Convert evaluation prompt into a TextMessage.
            cancellation_token=None, # No cancellation token needed.
        )
        # Trim and store the agent's evaluation of the draft response.
        evaluation = evaluation_response.chat_message.content.replace("TERMINATE", "").strip()
        # Determine if the evaluation indicates approval of the drafted answer.
        if evaluation.startswith("APPROVED"):
            # Return the content following "FINAL_ANSWER:" as the approved response.
            return evaluation.split("FINAL_ANSWER:", 1)[-1].strip()
        # Check if the evaluation indicates further revision is needed.
        if evaluation.startswith("REVISE"):
            # Capture feedback provided for further improvements.
            feedback = evaluation.split("FEEDBACK:", 1)[-1].strip()
        else:
            # Default feedback for revisions if none given.
            feedback = "Make the answer more conversational, first-person, natural, and grounded."
    # Return the final draft content if all attempts have been exhausted without approval.
    return draft_content
# Function to handle synchronous execution of the chat function by wrapping the async function.
def chat(message, history):
    return asyncio.run(chat_async(message, history)) # Runs the async chat_async function and yields the result.

# Creating a chat interface using Gradio, passing in the chat function as a callable.
demo = gr.ChatInterface(
    fn=chat,
    title="Chat with Samuel Gomez",
    description="Ask me about my background, projects, experience, skills, or anything you would normally ask after reading my resume.",
    examples=[
        "Tell me about yourself.",
        "What was your favorite technical project?",
        "How was your time at Purdue University?",
        "What kind of roles are you interested in?",
    ],
)

# The following block checks if the script is run as the main module, ensuring the app starts.
if __name__ == "__main__":
    demo.launch() # Launches the Gradio app to make the chat interface accessible to users.
