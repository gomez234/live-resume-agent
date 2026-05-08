"""
This file is responsible for establishing a database connection using the PostgreSQL library 'psycopg' 
and loading configuration variables from a .env file. It checks for the required DATABASE_URL 
environment variable and registers the pgvector extension with the database connection. 

The flow of the file begins with importing necessary libraries, then loading environment variables, 
and finally defining a function called get_connection() that performs the connection setup. 

The expected input is the DATABASE_URL, which should be present in a .env file in the format 
DATABASE_URL='your_database_url'. 

The output is a database connection object that can be used to interact with the PostgreSQL database. 
This function raises an error if the DATABASE_URL is not found, which helps in preventing 
misconfiguration issues when trying to connect.
"""
# Import the necessary libraries for the functionality of the application.
import os 
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

# Load environment variables from a .env file into the current process. 
# The 'override=True' argument ensures that existing environment variables are replaced by those defined in .env.
load_dotenv(override=True)

# Define a function named 'get_connection' to create and return a connection to the PostgreSQL database
def get_connection():
    # Retrieve the DATABASE_URL from the environment variables loaded from the .env file
    database_url = os.getenv("DATABASE_URL")
    # Check if the DATABASE_URL was not set; if so, raise an error to inform the user of the issue.
    if not database_url:
        raise ValueError("DATABASE_URL is missing from .env")
    # Establish a connection to the PostgreSQL database using the retrieved database_url.
    conn = psycopg.connect(database_url)
    # Register the pgvector extension with the created database connection to enable handling vector types.
    register_vector(conn)
    # Return the established database connection object so it can be used by the caller.
    return conn
