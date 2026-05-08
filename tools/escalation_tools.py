import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

from database import get_connection

load_dotenv(override=True)


def save_escalation(question: str, user_email: str | None, reason: str | None):
    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            """
            insert into escalations (question, user_email, reason)
            values (%s, %s, %s)
            """,
            (question, user_email, reason),
        )

    conn.commit()
    conn.close()


def send_escalation_email(question: str, user_email: str | None, reason: str | None):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    email_from = os.getenv("NOTIFY_EMAIL_FROM")
    email_password = os.getenv("NOTIFY_EMAIL_PASSWORD")
    email_to = os.getenv("NOTIFY_EMAIL_TO")

    if not all([smtp_host, email_from, email_password, email_to]):
        raise ValueError("Missing email settings in .env")

    msg = EmailMessage()
    msg["Subject"] = "Live Resume Agent - Unanswered Question"
    msg["From"] = email_from
    msg["To"] = email_to

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

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(email_from, email_password)
        server.send_message(msg)


def handle_escalation_submission(question: str, user_email: str | None, reason: str | None):
    save_escalation(question, user_email, reason)
    send_escalation_email(question, user_email, reason)