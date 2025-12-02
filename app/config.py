import os
from dotenv import load_dotenv

# Load .env file if present (local dev)
load_dotenv()

APP_MODE = os.getenv("APP_MODE", "local")  # "local" or "aws"
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
S3_BUCKET = os.getenv("S3_BUCKET", "axrail-bot-content")
CONTENT_MANIFEST_KEY = os.getenv("CONTENT_MANIFEST_KEY", "current.json")

BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "amazon.nova-lite-v1:0",
)
