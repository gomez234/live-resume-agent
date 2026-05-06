import re
from tools.document_loader import load_documents


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


def clean_words(text: str) -> set[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = text.split()

    stop_words = {
        "the", "and", "for", "with", "that", "this", "from", "are", "was",
        "you", "your", "about", "what", "how", "tell", "me", "did", "does",
        "his", "her", "him", "she", "they", "them", "have", "has", "had",
        "a", "an", "to", "of", "in", "on", "at", "by", "is", "it", "as"
    }

    return {word for word in words if word not in stop_words and len(word) > 2}


DOCUMENT_TEXT = load_documents()
CHUNKS = chunk_text(DOCUMENT_TEXT)


def retrieve_context(question: str, top_k: int = 4) -> str:
    question_words = clean_words(question)

    scored_chunks = []

    for chunk in CHUNKS:
        chunk_words = clean_words(chunk)
        score = len(question_words.intersection(chunk_words))

        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(reverse=True, key=lambda item: item[0])

    top_chunks = [chunk for score, chunk in scored_chunks[:top_k]]

    if not top_chunks:
        return ""

    return "\n\n--- Relevant Context ---\n\n".join(top_chunks)