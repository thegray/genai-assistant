import boto3, json
from typing import List, Tuple
from .config import S3_BUCKET, CONTENT_MANIFEST_KEY, APP_MODE
from .models import Chunk
from app.logger import logger

s3 = boto3.client("s3")
CHUNKS: List[Chunk] | None = None
CURRENT_KEY: str | None = None
LOCAL_CONTENT_FILE = "local_content.json"

def _load_manifest() -> str:
    obj = s3.get_object(Bucket=S3_BUCKET, Key=CONTENT_MANIFEST_KEY)
    manifest = json.loads(obj["Body"].read().decode("utf-8"))
    return manifest["current_key"]

def _load_chunks_from_s3(key: str) -> List[Chunk]:
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    data = json.loads(obj["Body"].read().decode("utf-8"))
    return [Chunk(**c) for c in data]

def _load_chunks_local():
    with open(LOCAL_CONTENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Chunk(**c) for c in data]

def get_chunks() -> Tuple[List[Chunk], str]:
    global CHUNKS, CURRENT_KEY

    if APP_MODE == "local":
        if CHUNKS is None:
            logger.info("loading chunks in local mode", extra={"source": "local_content.json"})
            CHUNKS = _load_chunks_local()
            CURRENT_KEY = "local"
        else:
            logger.debug("using cached chunks in local mode")
        return CHUNKS, CURRENT_KEY

    new_key = _load_manifest()
    logger.debug("fetched content manifest from S3", extra={"manifest_key": CONTENT_MANIFEST_KEY, "content_key": new_key})

    if CHUNKS is None:
        logger.info("cold start: loading chunks from S3", extra={"content_key": new_key})
        CHUNKS = _load_chunks_from_s3(new_key)
        CURRENT_KEY = new_key
    elif CURRENT_KEY != new_key:
        logger.info("content updated: reloading chunks from S3", extra={
            "old_key": CURRENT_KEY,
            "new_key": new_key,
        })
        CHUNKS = _load_chunks_from_s3(new_key)
        CURRENT_KEY = new_key
    else:
        logger.debug("using cached chunks, no manifest change", extra={"content_key": CURRENT_KEY})

    return CHUNKS, CURRENT_KEY

