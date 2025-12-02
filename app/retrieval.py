from typing import List
from .models import Chunk

def score_chunk(chunk: Chunk, query: str) -> int:
    q_words = set(query.lower().split())
    text_lower = chunk.text.lower()
    return sum(1 for w in q_words if w in text_lower)


def find_relevant_chunks(chunks: List[Chunk], query: str, top_k: int = 5) -> List[Chunk]:
    scored = [(score_chunk(c, query), c) for c in chunks]
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [c for _, c in scored[:top_k]]
    return top
