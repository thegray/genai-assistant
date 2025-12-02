import boto3, json, os
from .config import AWS_REGION, BEDROCK_MODEL_ID, APP_MODE
from app.logger import logger

_bedrock = None

def _get_bedrock_client():
    global _bedrock

    if _bedrock is None:
        bedrock_region = os.getenv("BEDROCK_REGION", AWS_REGION)
        logger.info(
            "creating Bedrock client",
            extra={"aws_region": AWS_REGION, "bedrock_region": bedrock_region},
        )
        _bedrock = boto3.client("bedrock-runtime", region_name=bedrock_region)

    return _bedrock

def generate_answer(prompt: str) -> str:
    if APP_MODE == "local":
        logger.debug("using mock LLM for local mode", extra={"mode": "local"})
        return _generate_answer_local(prompt)

    logger.info("calling Amazon Bedrock LLM", extra={
        "mode": APP_MODE,
        "model_id": BEDROCK_MODEL_ID,
    })
    logger.debug(f"using prompt: {prompt[:200]}...")
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ],
            }
        ],
        "max_tokens": 512,
        "temperature": 0.2,
        "top_p": 0.9,
    }

    client = _get_bedrock_client()

    try:
        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
    except Exception as e:
        logger.error("failed Bedrock invocation", extra={"error": str(e)})
        raise e 
    
    # Claude 3 response format:
    # {
    #   "id": "...",
    #   "type": "message",
    #   "role": "assistant",
    #   "content": [ { "type": "text", "text": "..." } ],
    #   ...
    # }
    try:
        response_body = json.loads(response["body"].read())
        content = response_body.get("content", [])
        if not content or "text" not in content[0]:
            logger.error(
                "unexpected Bedrock response format",
                extra={"body_snippet": str(response_body)[:400]},
            )
            return "failed generate response from the model."

        answer = content[0]["text"].strip()
    except Exception as e:
        logger.error("failed to parse Bedrock response", extra={"error": str(e)})
        return "failed understanding the model's response."

    logger.info(
        "received response from Bedrock",
        extra={"answer_preview": answer[:200]},
    )
    return answer

def _generate_answer_local(prompt: str) -> str:
    return "This is a mock answer from local"
