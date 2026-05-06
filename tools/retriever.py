from dotenv import load_dotenv
from openai import OpenAI
from tools.document_loader import load_documents
import numpy as np

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

def cosine_similarity(vector_a, vector_b) -> float:
    a = np.array(vector_a)
    b = np.array(vector_b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


DOCUMENT_TEXT = load_documents()
CHUNKS = chunk_text(DOCUMENT_TEXT)

print(f"Loaded {len(CHUNKS)} document chunks.")

CHUNK_EMBEDDINGS = [embed_text(chunk) for chunk in CHUNKS]

print("Document embeddings created.")


def retrieve_context(question: str, top_k: int = 4) -> str:
    question_embedding = embed_text(question)

    scored_chunks = []

    for chunk, chunk_embedding in zip(CHUNKS, CHUNK_EMBEDDINGS):
        score = cosine_similarity(question_embedding, chunk_embedding)
        scored_chunks.append((score, chunk))

    scored_chunks.sort(reverse=True, key=lambda item: item[0])

    top_chunks = [chunk for score, chunk in scored_chunks[:top_k]]

    return "\n\n--- Relevant Context ---\n\n".join(top_chunks)