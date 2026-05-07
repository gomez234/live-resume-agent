"""
This Python script is designed to load documents, chunk the text into smaller pieces, generate text embeddings using the OpenAI API, and store these embeddings in a database. 
The workflow begins by loading environment variables from a .env file, then sets up an OpenAI client. 
It retrieves documents, breaks them into manageable chunks, computes embeddings for each chunk, and finally inserts the chunks along with their embeddings into a database table. 
The script expects to find documents in a predefined location and requires access to a database where it can store the results. 
Upon completion, it reports the total number of chunks created and confirms that the documents are stored correctly.
"""

# Import the necessary libraries for the functionality of the application.
from openai import OpenAI
from dotenv import load_dotenv

# Importing the get_connection function from the database module.
from database import get_connection

# Importing the load_docunents function from the document_loader module.
from tools.document_loader import load_documents

# Load environment variables, allowing values in the .env file to override existing ones.
load_dotenv(override=True)

# Instantiate the OpenAI client which will be used to call the OpenAI API methods.
client = OpenAI()

# Define a function that takes a text string and chunks it into smaller pieces.
def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    # Initialize an empty list to hold the text chunks.
    chunks = []
    # Set the starting index for chunking to zero.
    start = 0
    # Loop to create text chunks until the entire text has been processed.
    while start < len(text):
        # Define the end index for the current chunk based on the start index and specified chunk size.
        end = start + chunk_size
        # Extract the chunk from the text, removing leading and trailing whitespace.
        chunk = text[start:end].strip()
        # Check if the chunk is not empty before appending to the list of chunks.
        if chunk:
            # Add the non-empty chunk to the list of chunks.
            chunks.append(chunk)
        # Update the start index to create an overlap for the next chunk.
        start += chunk_size - overlap
    # Return the list of created chunks.
    return chunks

# Define a function that generates embeddings for a given text using the OpenAI API.
def embed_text(text: str) -> list[float]:
    # Call the OpenAI API to create embeddings for the input text using a specified model.
    response = client.embeddings.create(
        model="text-embedding-3-small", # Specify the model to be used for generating embeddings.
        input=text, # Provide the text input for which the embedding is to be generated.
    )
    # Extract and return the embedding from the API response (first element of the returned data).
    return response.data[0].embedding

# Define the main function that orchestrates the execution of the script.
def main():
    # Inform the user that document loading is starting.
    print("Loading documents...")
    # Load the documents' text content using the load_documents function.
    document_text = load_documents()
    # Chunk the loaded document text into manageable pieces.
    chunks = chunk_text(document_text)
    # Notify the user of how many chunks were created from the document.
    print(f"Created {len(chunks)} chunks.")
    # Establish a connection to the database.
    conn = get_connection()
    # Create a cursor object to interact with the database connection.
    with conn.cursor() as cur:
        # Inform the user that old chunks are being cleared from the database.
        print("Clearing old chunks...")
        # Execute a SQL command to delete existing entries in the `resume_chunks` table.
        cur.execute("delete from resume_chunks;")
        # Iterate over the generated chunks with an index that starts at 1.
        for i, chunk in enumerate(chunks, start=1):
            # Inform the user of the current chunk being processed.
            print(f"Inserting chunk {i}/{len(chunks)}")
            # Generate an embedding for the current chunk of text.
            embedding = embed_text(chunk)
            # Execute a SQL INSERT command to add the new chunk and its associated embedding to the database.
            cur.execute(
                """
                insert into resume_chunks (source, content, embedding)
                values (%s, %s, %s)
                """,
                ("local_documents", chunk, embedding),
            )
    # Commit the transaction to save all changes made to the database.
    conn.commit()
    # Close the database connection to free any resources.
    conn.close()
    # Notify the user that the operation is complete and documents are stored.
    print("Done. Documents are now stored in Supabase pgvector.")

# This block checks if the script is being run directly and not imported as a module.
if __name__ == "__main__":
    # Call the main function to execute the script's main functionality.
    main()