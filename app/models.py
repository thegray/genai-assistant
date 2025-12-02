from pydantic import BaseModel
from typing import List, Optional

class Chunk(BaseModel):
    id: str
    url: str
    title: str
    text: str
    order: int

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Chunk]
