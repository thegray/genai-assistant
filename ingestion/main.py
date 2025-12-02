from ingestion.crawler import fetch_page, extract_text
from ingestion.content_handler import chunk_text
from ingestion.client import upload_chunks
from ingestion.link_discovery import discover_internal_links
from app.models import Chunk
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

INGESTION_MODE = os.getenv("INGESTION_MODE", "local")  # local | s3 | both

def main():
    start_urls = ["https://www.axrail.ai"]
    urls = discover_internal_links(start_urls, max_depth=2, max_pages=50)
    print(f"Discovered {len(urls)} URLs:")
    for u in urls:
        print(" -", u)

    all_chunks: list[Chunk] = []

    for url in urls:
        html = fetch_page(url)
        text = extract_text(html)
        chunks = chunk_text(url=url, title=url, text=text)
        all_chunks.extend(chunks)

    data = [c.model_dump() for c in all_chunks]

    if INGESTION_MODE in ("local", "both"):
        Path("local_content.json").write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )
        print(f"[local] wrote {len(all_chunks)} chunks to local_content.json")

    if INGESTION_MODE in ("s3", "both"):
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        content_key = f"content-{ts}.json"
        upload_chunks(all_chunks, content_key)
        print(f"[s3] uploaded {len(all_chunks)} chunks to S3 key: {content_key}")


if __name__ == "__main__":
    main()
