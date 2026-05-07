"""
This Python file is designed to interact with OpenAI's API to generate text embeddings 
and retrieve relevant context based on those embeddings. The flow of the program first 
loads environment variables, initializes a connection to the OpenAI API, and defines 
two main functions: embed_text and retrieve_context. 

The embed_text function takes a string input (text) and returns a list of floating-point 
numbers representing the text's embedding in vector format. The retrieve_context function 
accepts a question string and an optional integer (top_k) specifying how many relevant 
results to return. It fetches the top_k most similar text chunks from a database based 
on their embeddings, returning these results formatted for readability. 

The inputs expected are: 
- A string for text in embed_text, and 
- A string for question and an optional integer for top_k in retrieve_context.

The output is a formatted string of the most relevant context or an empty string if no 
relevant context is found. Database connection is also handled as a side effect.
"""

# Import the necessary libraries for the functionality of the application.
from dotenv import load_dotenv
from openai import OpenAI

# Importing the get_connection function from the database module.
from database import get_connection

# Loading environment variables from a .env file.
# The 'override=True' argument allows loading the variables even if they are already set.
load_dotenv(override=True)

# Initializing the OpenAI client to enable API calls.
# This client will be used to generate text embeddings.
client = OpenAI()

# Defining a function called embed_text that takes a single parameter `text` of type str.
# This function will create an embedding for the given text and return it as a list of floats.
def embed_text(text: str) -> list[float]:
    # Calling the OpenAI API to create embeddings for the input text.
    response = client.embeddings.create(
        model="text-embedding-3-small",  # The 'model' specifies which embedding model to use.
        input=text, # Passing the input text for which embeddings will be generated.
    )
    # Returning the embedding vector from the API response.
    return response.data[0].embedding

# Defining a function called retrieve_context that takes two parameters: `question` (str)
# and an optional parameter `top_k` (int) with a default value of 5. 
# This function will fetch relevant text chunks based on the similarity of their embeddings.
def retrieve_context(question: str, top_k: int = 5) -> str:
    # Generating the embedding for the input question by calling the embed_text function.
    question_embedding = embed_text(question)
    # Establishing a connection to the database using the get_connection function.
    conn = get_connection()
    # Using a context manager to ensure that the database cursor is properly managed.
    with conn.cursor() as cur:
        # Executing a SQL query to fetch content and calculate similarity based on the question's embedding.
        cur.execute(
            """
            select content, 1 - (embedding <=> %s::vector) as similarity
            from resume_chunks
            order by embedding <=> %s::vector
            limit %s;
            """,
            (question_embedding, question_embedding, top_k), # Parameterizing the query to safely insert the question_embedding and top_k values.
        )
        # Fetching all rows returned by the query.
        rows = cur.fetchall()
    # Closing the database connection after the operation is complete.
    conn.close()
    # Checking if there are any rows returned from the SQL query. 
    # If there are no rows (i.e., no similar content found), return an empty string.
    if not rows:
        return ""
    # Initializing an empty list to store formatted chunks of relevant content.
    chunks = []
    # Iterating through each row of fetched data containing content and similarity score.
    for content, similarity in rows:
        # Appending a formatted string to the chunks list.
        # This string includes the similarity score formatted to three decimal places.
        chunks.append(
            f"[Similarity: {similarity:.3f}]\n{content}"
        )
    # Joining all formatted chunks into a single string with section headers 
    # and returning it as the result of the function.
    return "\n\n--- Relevant Context ---\n\n".join(chunks)