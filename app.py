#Import the necessary libraries
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

#Load the environment variables
load_dotenv()

#Initialize the OpenAI client
client = OpenAI()

#Define the system prompt
SYSTEM_PROMPT = """
You are Samuel Gomez's Live Resume Agent. Samuel is a funny and engaging person.

You answer questions as Samuel Gomez, using a professional, friendly, and concise tone.

For this first version, you know these general facts:
- Samuel has experience in data analytics, AI, automation, and business technology.
- He has worked on projects involving Power BI, Python, Azure, SharePoint, Power Automate, and agentic AI.
- He has experience with internships, research projects, dashboards, and technical documentation.
- He is interested in data analytics, AI, business program management, and technology-driven business solutions.

Important rules:
- Do not invent specific details.
- If you are unsure, say that Samuel can provide more information directly.
- Keep answers clear and professional.
"""
#Define the chat function
def chat(message, history):
    #Create the messages list
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    #Add the history to the messages list
    for item in history:
        #Add the role and content to the messages list
        messages.append({"role": item["role"], "content": item["content"]})
    
    #Add the user message to the messages list
    messages.append({"role": "user", "content": message})

    #Generate the response
    #Use the OpenAI client to generate the response
    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)

    #Return the response
    return response.choices[0].message.content

#Define the Gradio interface
demo = gr.ChatInterface(
    #Define the function to call when the user sends a message
    fn=chat,
    #Define the title of the interface
    title="Samuel Gomez's Live Resume Agent",
    #Define the description of the interface
    description="Ask questions about Samuel's background, projects, experience, and skills.",
    #Define the examples of the interface
    examples=[
        "Tell me about Samuel's technical skills.",
        "What kind of projects has Samuel worked on?",
        "What makes Samuel a strong candidate?",
    ],
)
#Run the interface  
#If the script is run directly, launch the interface        
if __name__ == "__main__":
    demo.launch()