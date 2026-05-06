from dotenv import load_dotenv
from openai import OpenAI

from database import get_connection

load_dotenv(override=True)

client = OpenAI()


def embed_text(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def retrieve_context(question: str, top_k: int = 5) -> str:
    question_embedding = embed_text(question)

    conn = get_connection()

    with conn.cursor() as cur:
        cur.execute(
            """
            select content, 1 - (embedding <=> %s::vector) as similarity
            from resume_chunks
            order by embedding <=> %s::vector
            limit %s;
            """,
            (question_embedding, question_embedding, top_k),
        )

        rows = cur.fetchall()

    conn.close()

    if not rows:
        return ""

    chunks = []

    for content, similarity in rows:
        chunks.append(
            f"[Similarity: {similarity:.3f}]\n{content}"
        )

    return "\n\n--- Relevant Context ---\n\n".join(chunks)