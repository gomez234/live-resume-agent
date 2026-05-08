"""
This file handles the submission of escalations related to unanswered questions.
It provides functionality to save the escalation data to a database and send a notification email about it.
The expected inputs are:
- A string that contains the unanswered question.
- An optional string that holds the user's email address; can be None.
- An optional string that gives a reason for the escalation; can also be None.
Outputs include:
- The escalation data saved in a database.
- An email sent to a specified recipient notifying them of the escalation.
"""

#Import the necessary libraries
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Importing the get_connection function from the database module.
from database import get_connection

# Loads environment variables from a .env file, allowing existing variables to be overridden.
load_dotenv(override=True)

def save_escalation(question: str, user_email: str | None, reason: str | None):
    """
    Saves the escalation details into the database.
    
    Parameters:
    - The unanswered question being escalated.
    - The email of the user asking the question; can be None.
    - The reason for the escalation; can be None.
    """
    # Calls get_connection to establish a connection to the database.
    conn = get_connection()
    # Creates a cursor object to interact with the database and ensures proper cleanup.
    with conn.cursor() as cur:
        # Executes the SQL command to insert the escalation details into the escalations table.
        cur.execute(
            """
            insert into escalations (question, user_email, reason)
            values (%s, %s, %s)
            """,
            (question, user_email, reason),
        )
    # Commits the transaction to save the changes in the database.
    conn.commit()
    # Closes the database connection to free up resources.
    conn.close()

def send_escalation_email(question: str, user_email: str | None, reason: str | None):
    """
    Sends an email notification about the escalation.
    
    Parameters:
    - The unanswered question being escalated.
    - The email of the user asking the question; can be None.
    - The reason for the escalation; can be None.
    """
    # Retrieves the SMTP host from environment variables.
    smtp_host = os.getenv("SMTP_HOST")
    # Retrieves and converts the SMTP port to an integer; defaults to 587.
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    # Gets the sender's email address from environment variables.
    email_from = os.getenv("NOTIFY_EMAIL_FROM")
    # Retrieves the email account password from environment variables.
    email_password = os.getenv("NOTIFY_EMAIL_PASSWORD")
    # Gets the recipient's email address from environment variables.
    email_to = os.getenv("NOTIFY_EMAIL_TO")
    # Checks if any required email settings are missing.
    if not all([smtp_host, email_from, email_password, email_to]):
        # Raises an error if any email settings are not found.
        raise ValueError("Missing email settings in .env")
    # Creates a new instance of EmailMessage to construct the email.
    msg = EmailMessage()
    # Sets the email subject line.
    msg["Subject"] = "Live Resume Agent - Unanswered Question"
    # Specifies the sender's email address.
    msg["From"] = email_from
    # Specifies the recipient's email address.
    msg["To"] = email_to
    # Sets the email's body content, including the question, user email, and reason for escalation.
    msg.set_content(
        f"""
A visitor asked a question that should be answered directly.

Question:
{question}

Visitor email:
{user_email or "Not provided"}

Reason:
{reason or "No reason provided"}
        """
    )
    # Creates an SMTP server instance using the provided host and port.
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        # Upgrades the connection to a secure encrypted SSL/TLS connection.
        server.starttls()
        # Logs into the SMTP server using the sender's email credentials.
        server.login(email_from, email_password)
        # Sends the constructed email message.
        server.send_message(msg)

def handle_escalation_submission(question: str, user_email: str | None, reason: str | None):
    """
    Handles the complete escalation submission process.
    
    It saves the escalation data and sends an email notification.
    
    Parameters:
    - The unanswered question being escalated.
    - The email of the user asking the question; can be None.
    - The reason for the escalation; can be None.
    """
    # Invokes the save_escalation function to store data in the database.
    save_escalation(question, user_email, reason)
    # Calls send_escalation_email to notify through email.
    send_escalation_email(question, user_email, reason)