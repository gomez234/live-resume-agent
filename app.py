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

# Importing a function that retrieves relevant context based on user questions.
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

def looks_like_email(text: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", text.strip()) is not None
pending_escalation = {
    "active": False,
    "question": None,
    "reason": None,
}


async def chat_async(message, history):
    global pending_escalation

    if pending_escalation["active"]:
        if looks_like_email(message):
            user_email = message.strip()

            handle_escalation_submission(
                question=pending_escalation["question"],
                user_email=user_email,
                reason=pending_escalation["reason"],
            )

            pending_escalation = {
                "active": False,
                "question": None,
                "reason": None,
            }

            return "Perfect — thanks for sharing your email. I’ll make sure Samuel sees your question and can follow up directly."

        return "That looks like something other than an email. Could you please send the best email address for Samuel to follow up?"

    router_response = await router_agent.on_messages(
        [TextMessage(content=message, source="user")],
        cancellation_token=None,
    )

    route = router_response.chat_message.content.replace("TERMINATE", "").strip()

    if route == "WEB_SEARCH":
        web_response = await web_search_agent.on_messages(
            [TextMessage(content=message, source="user")],
            cancellation_token=None,
        )
        relevant_context = web_response.chat_message.content.replace("TERMINATE", "").strip()
    else:
        relevant_context = retrieve_context(message)

    escalation_prompt = f"""
User question:
{message}

Available context:
{relevant_context}

Should this question be escalated to Samuel directly?
"""

    escalation_response = await escalation_agent.on_messages(
        [TextMessage(content=escalation_prompt, source="user")],
        cancellation_token=None,
    )

    escalation_decision = escalation_response.chat_message.content.replace("TERMINATE", "").strip()

    if escalation_decision.startswith("ESCALATE"):
        reason = ""

        if "REASON:" in escalation_decision and "MESSAGE_TO_USER:" in escalation_decision:
            reason = escalation_decision.split("REASON:", 1)[-1].split("MESSAGE_TO_USER:", 1)[0].strip()

        pending_escalation = {
            "active": True,
            "question": message,
            "reason": reason,
        }

        if "MESSAGE_TO_USER:" in escalation_decision:
            message_to_user = escalation_decision.split("MESSAGE_TO_USER:", 1)[-1].strip()
        else:
            message_to_user = "I don’t have enough verified information to answer that confidently."

        return f"{message_to_user}\n\nWhat’s the best email where Samuel can follow up with you?"

    feedback = ""
    draft_content = ""

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

        draft_response = await answer_writer_agent.on_messages(
            [TextMessage(content=writer_prompt, source="user")],
            cancellation_token=None,
        )

        draft_content = draft_response.chat_message.content.replace("TERMINATE", "").strip()

        evaluator_prompt = f"""
User question:
{message}

Context:
{relevant_context}

Draft answer:
{draft_content}

Evaluate the answer.
"""

        evaluation_response = await evaluator_agent.on_messages(
            [TextMessage(content=evaluator_prompt, source="user")],
            cancellation_token=None,
        )

        evaluation = evaluation_response.chat_message.content.replace("TERMINATE", "").strip()

        if evaluation.startswith("APPROVED"):
            return evaluation.split("FINAL_ANSWER:", 1)[-1].strip()

        if evaluation.startswith("REVISE"):
            feedback = evaluation.split("FEEDBACK:", 1)[-1].strip()
        else:
            feedback = "Make the answer more conversational, first-person, natural, and grounded."

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
        "What did you work on at Microsoft?",
        "What kind of roles are you interested in?",
    ],
)

# The following block checks if the script is run as the main module, ensuring the app starts.
if __name__ == "__main__":
    demo.launch() # Launches the Gradio app to make the chat interface accessible to users.