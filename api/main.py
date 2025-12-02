from fastapi import FastAPI, HTTPException, Request
from app.logger import logger, set_request_id, reset_request_id
from app.models import ChatRequest, ChatResponse
from app.content_loader import get_chunks
from app.retrieval import find_relevant_chunks
from app.prompt_builder import build_prompt
from app.llm_client import generate_answer
import uuid, time

app = FastAPI(title="Axrail GenAI Assistant")

@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    # Use header if present, otherwise generate
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    token = set_request_id(req_id)

    start = time.time()

    try:
        response = await call_next(request)
    except Exception as e:
        raise e
    finally:
        duration_ms = round((time.time() - start) * 1000, 2)

        reset_request_id(token)

    return response

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
