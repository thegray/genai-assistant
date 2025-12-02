from fastapi import FastAPI, HTTPException
from app.models import ChatRequest, ChatResponse
from app.content_loader import get_chunks
from app.retrieval import find_relevant_chunks
from app.prompt_builder import build_prompt
from app.llm_client import generate_answer

app = FastAPI(title="Axrail GenAI Assistant")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    chunks, key = get_chunks()

    relevant = find_relevant_chunks(chunks, request.message)

    prompt = build_prompt(relevant, request.message)
    try:
        answer = generate_answer(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail="LLM call failed") from e

    return ChatResponse(answer=answer, sources=relevant)
