import boto3, json
from .config import AWS_REGION, BEDROCK_MODEL_ID, APP_MODE

def generate_answer(prompt: str) -> str:
    if APP_MODE == "local":
        return _generate_answer_local(prompt)

    body = {
        "prompt": {prompt},
        "max_tokens": 512,
        "temperature": 0.2,
    }

    global _bedrock
    if _bedrock is None:
        _bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    try:
        response = _bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
    except Exception as e:
        raise e

    response_body  = json.loads(response["body"].read())
    parsed_output = response_body.get('results')[0].get('outputText')
    return parsed_output

def _generate_answer_local(prompt: str) -> str:
    return "This is a mock answer from local"
