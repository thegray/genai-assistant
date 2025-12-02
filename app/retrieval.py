from typing import List
from .models import Chunk
from app.logger import logger

def score_chunk(chunk: Chunk, query: str) -> int:
    q_words = set(query.lower().split())
    text_lower = chunk.text.lower()
    return sum(1 for w in q_words if w in text_lower)

def find_relevant_chunks(chunks: List[Chunk], query: str, top_k: int = 5) -> List[Chunk]:
    logger.info("retrieving relevant chunks", extra={"query": query, "top_k": top_k})

    scored = [(score_chunk(c, query), c) for c in chunks]
    non_zero = [pair for pair in scored if pair[0] > 0]

    logger.debug("scoring chunks", extra={
        "total_chunks": len(chunks),
        "matched_chunks": len(non_zero),
    })

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [c for _, c in scored[:top_k]]

    logger.info(f"selected {len(top)} relevant chunks", extra={"selected_count": len(top)})
    return top
