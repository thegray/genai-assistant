import json
import boto3
from typing import List
from app.models import Chunk
from app.config import S3_BUCKET

s3 = boto3.client("s3")

def upload_chunks(chunks: List[Chunk], content_key: str, manifest_key: str = "current.json"):
    data = [c.model_dump() for c in chunks]
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=content_key,
        Body=json.dumps(data).encode("utf-8"),
        ContentType="application/json",
    )

    manifest = {"current_key": content_key}
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=manifest_key,
        Body=json.dumps(manifest).encode("utf-8"),
        ContentType="application/json",
    )
