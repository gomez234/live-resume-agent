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

# Importing various agent creation functions for different roles in the chat application.
from agents.answer_writer_agent import create_answer_writer_agent
from agents.evaluator_agent import create_tone_evaluator_agent
from agents.router_agent import create_router_agent
from agents.web_search_agent import create_web_search_agent
from agents.escalation_agent import create_escalation_agent

# Importing a function that retrieves relevant context based on user questions.
from tools.retriever import retrieve_context

# Load the environment variables from a .env file, allowing configuration without hardcoding sensitive information.
# The override=True option allows existing variables to be overridden by values in the .env file.
load_dotenv(override=True)

# Instantiating various agents using the respective creation functions.
router_agent = create_router_agent()
web_search_agent = create_web_search_agent()
answer_writer_agent = create_answer_writer_agent()
evaluator_agent = create_tone_evaluator_agent()
escalation_agent = create_escalation_agent()

# Asynchronous function to handle user chat messages and generate responses based on them.
async def chat_async(message, history):
    # Sending the user message to the router agent to obtain the response about which agent to use.
    router_response = await router_agent.on_messages(
    [TextMessage(content=message, source="user")], # Packaging the user message into a TextMessage object.
    cancellation_token=None, # No cancellation token is passed here, meaning the operation would not be cancellable.
    )
    # Extracting the content from the router response and cleaning it of any 'TERMINATE' signal.
    route = router_response.chat_message.content.replace("TERMINATE", "").strip()
    # If the router suggests a web search, interface with the web search agent.
    if route == "WEB_SEARCH":
        web_response = await web_search_agent.on_messages(
        [TextMessage(content=message, source="user")], # Send the message to the web search agent.
        cancellation_token=None, # Again, no cancellation token is provided.
        )
        # Clean the web search response and prepare relevant context for the answer writer.
        relevant_context = web_response.chat_message.content.replace("TERMINATE", "").strip()
    else:
        # If not a web search, retrieve context using a custom function that searches for necessary information.
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
        if "MESSAGE_TO_USER:" in escalation_decision:
            return escalation_decision.split("MESSAGE_TO_USER:", 1)[-1].strip()

        return "I don't have enough verified information to answer that confidently. This is something I should answer directly."
    # Initialize variables to accumulate feedback and draft content during response generation.
    feedback = ""
    draft_content = ""
     # Attempt to generate satisfactory answers up to three times.
    for attempt in range(3):
        # Preparing a prompt that includes relevant context and previous feedback to guide the answer writer.
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
         # Sending the writer prompt to the answer writer agent to generate a draft answer.
        draft_response = await answer_writer_agent.on_messages(
            [TextMessage(content=writer_prompt, source="user")],  # Package the writer prompt into a TextMessage object.
            cancellation_token=None, # No cancellation token is provided.
        )
        # Extract the content of the draft response and clean it for any 'TERMINATE' signal.
        draft_content = draft_response.chat_message.content.replace("TERMINATE", "").strip()
        # Prepare an evaluation prompt that sends the user question, context, and draft answer to the evaluator agent.
        evaluator_prompt = f"""
            User question:
            {message}

            Verified context:
            {relevant_context}

            Draft answer:
            {draft_content}

            Evaluate the answer.
        """
        # Send the evaluation prompt to the evaluator agent for feedback on the draft answer.
        evaluation_response = await evaluator_agent.on_messages(
            [TextMessage(content=evaluator_prompt, source="user")], # Packaging the evaluation prompt in a TextMessage.
            cancellation_token=None, # No cancellation token is provided.
        )
         # Extract and clean the evaluation result from the evaluator's response.
        evaluation = evaluation_response.chat_message.content.replace("TERMINATE", "").strip()
        # If the evaluation indicates the answer is approved, extract and return the final answer.
        if evaluation.startswith("APPROVED"):
            final_answer = evaluation.split("FINAL_ANSWER:", 1)[-1].strip()  # Get the text after 'FINAL_ANSWER:'.
            return final_answer # Return the satisfactory answer to the user.
        # If the evaluation requests a revision, extract the feedback for improving the answer.
        if evaluation.startswith("REVISE"):
            feedback = evaluation.split("FEEDBACK:", 1)[-1].strip() # Get the feedback provided by the evaluator.
        else:
            # Default feedback if the evaluation is not specific; instructs for a more conversational answer.
            feedback = "Make the answer more conversational, first-person, natural, and grounded."
    # If no satisfactory answer is produced after three attempts, return the latest draft content.
    return draft_content # Returns the last draft content as a fallback response.

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