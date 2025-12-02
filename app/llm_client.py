import boto3, json
from .config import AWS_REGION, BEDROCK_MODEL_ID, APP_MODE
from app.logger import logger

def generate_answer(prompt: str) -> str:
    if APP_MODE == "local":
        logger.debug("using mock LLM for local mode", extra={"mode": "local"})
        return _generate_answer_local(prompt)

    logger.info("calling Amazon Bedrock LLM")
    logger.debug(f"using prompt: {prompt[:200]}...")
    body = {
        "prompt": {prompt},
        "max_tokens": 512,
        "temperature": 0.2,
    }

    global _bedrock
    if _bedrock is None:
        logger.info("creating Bedrock client", extra={"region": AWS_REGION})
        _bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    logger.info("invoking Bedrock LLM", extra={"model_id": BEDROCK_MODEL_ID})

    try:
        response = _bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
    except Exception as e:
        logger.error(f"failed bedrock invocation: {e}")
        raise e

    response_body  = json.loads(response["body"].read())
    parsed_output = response_body.get('results')[0].get('outputText')
    logger.info(f"received response from Bedrock: {parsed_output}")
    return parsed_output

def _generate_answer_local(prompt: str) -> str:
    return "This is a mock answer from local"
