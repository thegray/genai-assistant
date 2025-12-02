from typing import List
from app.models import Chunk
import textwrap
import itertools

def chunk_text(url: str, title: str, text: str, max_chars: int = 800) -> List[Chunk]:
    parts = textwrap.wrap(text, max_chars)
    chunks: List[Chunk] = []
    for i, part in enumerate(parts):
        chunks.append(
            Chunk(
                id=f"{url}-{i}",
                url=url,
                title=title,
                text=part,
                order=i,
            )
        )
    return chunks
