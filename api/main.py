from fastapi import FastAPI, HTTPException, Request
from app.logger import logger, set_request_id, reset_request_id
from app.models import ChatRequest, ChatResponse
from app.content_loader import get_chunks
from app.retrieval import find_relevant_chunks
from app.prompt_builder import build_prompt
from app.llm_client import generate_answer
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import uuid, time

app = FastAPI(title="Axrail GenAI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # for dev: allow all
    allow_credentials=True,
    allow_methods=["*"],     # allows POST, OPTIONS, GET, etc.
    allow_headers=["*"],     # allows Content-Type, etc.
)

@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    # Use header if present, otherwise generate
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    token = set_request_id(req_id)

    logger.info("incoming request", extra={
        "path": request.url.path,
        "method": request.method,
        "request_id": req_id,
    })

    start = time.time()

    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"unhandled error during request {e}", extra={"request_id": req_id})
        raise e
    finally:
        duration_ms = round((time.time() - start) * 1000, 2)
        logger.info("request completed", extra={
            "path": request.url.path,
            "duration_ms": duration_ms,
            "request_id": req_id,
        })

        reset_request_id(token)

    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    logger.info("handling /chat", extra={"message_text": request.message})
    chunks, key = get_chunks()
    logger.debug("loaded chunks", extra={"content_version": key, "chunk_count": len(chunks)})

    relevant = find_relevant_chunks(chunks, request.message)
    logger.debug("selected relevant chunks", extra={
        "relevant_count": len(relevant),
        "titles": [c.title for c in relevant],
    })
    if not relevant:
        # fallback: maybe use some high-level chunks or a default message
        relevant = chunks[:3]
        logger.info("not found relevant chunks, using top 3", extra={"titles": [c.title for c in relevant]})

    prompt = build_prompt(relevant, request.message)
    try:
        answer = generate_answer(prompt)
    except Exception as e:
        logger.error(f"LLM call failed, error: {e}")
        raise HTTPException(status_code=500, detail="LLM call failed") from e

    logger.info("returning answer to client", extra={"answer_preview": answer[:120]})
    return ChatResponse(answer=answer, sources=relevant)

handler = Mangum(app)