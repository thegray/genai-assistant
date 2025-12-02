# Overview
Axrail Assistant is a GenAI-powered chatbot that answers questions based on content crawled from the Axrail website.

## Architecture
### Components
**Ingestion Pipeline** : crawls the source website, extracts contents, creates chunks, and uploads to S3 or stores locally in JSON format.

**Chat Service** : build with FastAPI and optionally runs on AWS Lambda.

**Frontend Web UI** : simple HTML/JS chat interface.

### Infrastructure Dependencies
- **Amazon Bedrock** provides the LLM for generative AI capabilities
- **Amazon S3** stores the crawled content files

## Local Development

### Installation
Install dependencies:
```bash
pip install -r requirements/chat_service.txt
```

### Configuration
Create a `.env` file with the following settings:
```
APP_MODE=local
INGESTION_MODE=local
LOG_LEVEL=DEBUG
```

### Running the Ingestion Pipeline
```bash
python -m ingestion.main
```
This generates `local_content.json` with the crawled content.

### Starting the Chat Service
```bash
uvicorn api.main:app
```

### Accessing the Web UI
Open `frontend/index.html` in your browser.

## AWS Lambda Deployment

### Environment Variables

Configure the following in Lambda:
```
APP_MODE=aws
AWS_REGION=ap-southeast-1
S3_BUCKET=axrail-bot-content
CONTENT_MANIFEST_KEY=current.json
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
LOG_LEVEL=INFO
```

### Building and Deploying
Install dependencies into the Lambda package:
```bash
pip install -r requirements/chat_service.txt -t lambda_package/
cp -r api/ app/ lambda_package/
cd lambda_package && zip -r ../deployment.zip .
```
Upload `deployment.zip` to Lambda.

### API Gateway Configuration
Configure a POST endpoint at `/chat` with Lambda proxy integration and enable CORS for the frontend.

### Frontend Configuration
Update the API URL in the web UI:
```javascript
const API_URL = "https://xxxx.execute-api.ap-southeast-1.amazonaws.com/chat";
```

## Website Crawler

### Running the Ingestion Pipeline
Crawl and upload content to S3:

```bash
INGESTION_MODE=s3 python -m ingestion.main
```
This uploads `content-<timestamp>.json` and updates `current.json` as a manifest pointer.

### Ingestion Modes
The crawler supports three modes:
- `INGESTION_MODE=local` writes to `local_content.json`
- `INGESTION_MODE=s3` uploads to S3
- `INGESTION_MODE=both` writes locally and uploads to S3

### How It Works
The ingestion process performs the following steps:
1. Discovers internal links within the axrail.ai domain
2. Fetches HTML content
3. Extracts readable text
4. Splits content into chunks
5. Generates `content-<timestamp>.json`
6. Uploads to S3 and updates `current.json`
7. Chat service or Lambda detects new content and reloads automatically

## Frontend
The web UI is a lightweight HTML/JS interface that calls the `/chat` endpoint to display conversation messages. It works seamlessly in both local development and deployed environments.