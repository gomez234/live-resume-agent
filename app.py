#Import the necessary libraries
import asyncio
from dotenv import load_dotenv
import gradio as gr
from autogen_agentchat.messages import TextMessage
from agents.identity_agent import create_identity_agent
from tools.document_loader import load_documents

DOCUMENT_CONTEXT = load_documents()

#Load the environment variables
load_dotenv(override=True)


identity_agent = create_identity_agent()

async def chat_async(message, history):
    full_prompt = f"""
Context about Samuel Gomez:
{DOCUMENT_CONTEXT}

User question:
{message}
"""
    response = await identity_agent.on_messages(
        [TextMessage(content=full_prompt, source="user")],
        cancellation_token=None,
    )

    return response.chat_message.content

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