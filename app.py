#Import the necessary libraries
import asyncio
from dotenv import load_dotenv
import gradio as gr
from autogen_agentchat.messages import TextMessage

from agents.answer_writer_agent import create_answer_writer_agent
from agents.evaluator_agent import create_tone_evaluator_agent
from agents.router_agent import create_router_agent
from agents.web_search_agent import create_web_search_agent

from tools.retriever import retrieve_context

#Load the environment variables
load_dotenv(override=True)

router_agent = create_router_agent()
web_search_agent = create_web_search_agent()
answer_writer_agent = create_answer_writer_agent()
evaluator_agent = create_tone_evaluator_agent()

async def chat_async(message, history):
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

    feedback = ""
    draft_content = ""

    for attempt in range(3):
        writer_prompt = f"""
Context from Samuel's verified documents:
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

Verified context:
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
            final_answer = evaluation.split("FINAL_ANSWER:", 1)[-1].strip()
            return final_answer

        if evaluation.startswith("REVISE"):
            feedback = evaluation.split("FEEDBACK:", 1)[-1].strip()
        else:
            feedback = "Make the answer more conversational, first-person, natural, and grounded."

    return draft_content

def chat(message, history):
    return asyncio.run(chat_async(message, history))

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

if __name__ == "__main__":
    demo.launch()