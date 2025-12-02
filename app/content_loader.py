import boto3, json
from typing import List, Tuple
from .config import S3_BUCKET, CONTENT_MANIFEST_KEY, APP_MODE
from .models import Chunk

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
            CHUNKS = _load_chunks_local()
            CURRENT_KEY = "local"
        return CHUNKS, CURRENT_KEY

    new_key = _load_manifest()

    if CHUNKS is None:
        CHUNKS = _load_chunks_from_s3(new_key)
        CURRENT_KEY = new_key
    elif CURRENT_KEY != new_key:
        CHUNKS = _load_chunks_from_s3(new_key)
        CURRENT_KEY = new_key

    return CHUNKS, CURRENT_KEY

