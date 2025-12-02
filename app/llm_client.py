import boto3, json
from .config import AWS_REGION, BEDROCK_MODEL_ID, APP_MODE
from app.logger import logger

_bedrock = None

def _get_bedrock_client():
    global _bedrock
    if _bedrock is None:
        logger.info("creating Bedrock client", extra={"region": AWS_REGION})
        _bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)
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
        "prompt": {prompt},
        "max_tokens": 512,
        "temperature": 0.2,
    }

    bedrock = _get_bedrock_client()

    try:
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
    except Exception as e:
        logger.error("failed Bedrock invocation", extra={"error": str(e)})
        raise e

    try:
        response_body = json.loads(response["body"].read())
        results = response_body.get("results") or []
        if not results:
            logger.error("Bedrock response has no results", extra={"body": response_body})
            return "Sorry, I couldn't generate a response from the model."

        parsed_output = results[0].get("outputText", "").strip()
    except Exception as e:
        logger.error("failed to parse Bedrock response", extra={"error": str(e)})
        return "failed understanding model's response"
    
    logger.info("received response from Bedrock", extra={
        "answer_preview": parsed_output[:200],
    })
    return parsed_output

def _generate_answer_local(prompt: str) -> str:
    return "This is a mock answer from local"
