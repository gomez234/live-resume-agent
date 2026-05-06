#Import the necessary libraries
import asyncio
from dotenv import load_dotenv
import gradio as gr
from autogen_agentchat.messages import TextMessage
from agents.identity_agent import create_identity_agent

#Load the environment variables
load_dotenv(override=True)

identity_agent = create_identity_agent()

async def chat_async(message, history):
    response = await identity_agent.on_messages(
        [TextMessage(content=message, source="user")],
        cancellation_token=None,
    )

    return response.chat_message.content

def chat(message, history):
    return asyncio.run(chat_async(message, history))

demo = gr.ChatInterface(
    fn=chat,
    title="Samuel Gomez's Live Resume Agent",
    description="Ask questions about Samuel's background, projects, experience, and skills.",
    examples=[
        "Tell me about Samuel's technical skills.",
        "What kind of projects has Samuel worked on?",
        "What makes Samuel a strong candidate?",
    ],
)

if __name__ == "__main__":
    demo.launch()