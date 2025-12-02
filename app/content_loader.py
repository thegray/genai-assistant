import boto3, json
from typing import List, Tuple
from .config import S3_BUCKET, CONTENT_MANIFEST_KEY
from .models import Chunk

s3 = boto3.client("s3")
CHUNKS: List[Chunk] | None = None
CURRENT_KEY: str | None = None

def _load_manifest() -> str:
    obj = s3.get_object(Bucket=S3_BUCKET, Key=CONTENT_MANIFEST_KEY)
    manifest = json.loads(obj["Body"].read().decode("utf-8"))
    return manifest["current_key"]

def _load_chunks(key: str) -> List[Chunk]:
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    data = json.loads(obj["Body"].read().decode("utf-8"))
    return [Chunk(**c) for c in data]

def get_chunks() -> Tuple[List[Chunk], str]:
    global CHUNKS, CURRENT_KEY

    new_key = _load_manifest()

    if CHUNKS is None:
        CHUNKS = _load_chunks(new_key)
        CURRENT_KEY = new_key
    elif CURRENT_KEY != new_key:
        CHUNKS = _load_chunks(new_key)
        CURRENT_KEY = new_key
    else:
        print("using cached chunks, no manifest change")

    return CHUNKS, CURRENT_KEY

