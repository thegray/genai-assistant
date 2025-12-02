from typing import List
from .models import Chunk

BASE_SYSTEM_PROMPT = """
You are an AI assistant for Axrail, a cloud and data analytics company.
Use only the provided website content to answer.
If the information is not present, say you couldn't find it on the Axrail website.
"""


def build_prompt(chunks: List[Chunk], query: str) -> str:
    context_text = "\n\n".join(
        f"[{c.title} - {c.url}]\n{c.text}" for c in chunks
    )

    return f"""{BASE_SYSTEM_PROMPT}

Context:
{context_text}

User question:
{query}
"""
