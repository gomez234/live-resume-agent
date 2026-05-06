from openai import OpenAI
from dotenv import load_dotenv

from database import get_connection
from tools.document_loader import load_documents

load_dotenv(override=True)

client = OpenAI()


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def embed_text(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def main():
    print("Loading documents...")
    document_text = load_documents()
    chunks = chunk_text(document_text)

    print(f"Created {len(chunks)} chunks.")

    conn = get_connection()

    with conn.cursor() as cur:
        print("Clearing old chunks...")
        cur.execute("delete from resume_chunks;")

        for i, chunk in enumerate(chunks, start=1):
            print(f"Inserting chunk {i}/{len(chunks)}")
            embedding = embed_text(chunk)

            cur.execute(
                """
                insert into resume_chunks (source, content, embedding)
                values (%s, %s, %s)
                """,
                ("local_documents", chunk, embedding),
            )

    conn.commit()
    conn.close()

    print("Done. Documents are now stored in Supabase pgvector.")


if __name__ == "__main__":
    main()