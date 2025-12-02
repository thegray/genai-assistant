import boto3, json
from .config import AWS_REGION, BEDROCK_MODEL_ID

def generate_answer(prompt: str) -> str:
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
