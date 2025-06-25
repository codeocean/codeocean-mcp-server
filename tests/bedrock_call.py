# bedrock_call.py
import os
from typing import Any, Dict, List

import boto3
from bedrock_tools_converter import convert_tool_format

# DEFAULT_MODEL = "amazon.nova-pro-v1:0"
DEFAULT_MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"
BEDROCK_PROFILE = os.getenv("BEDROCK_PROFILE")
REGION = os.getenv("REGION")

session = boto3.Session(profile_name=BEDROCK_PROFILE)
client = session.client("bedrock-runtime", region_name=REGION)


def call_bedrock(
    prompt: str,
    tools: List[Dict[str, Any]] | None = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
) -> Dict[str, Any]:
    """Send prompt (and optional tools) to Amazon Bedrock via the Converse API."""
    payload: Dict[str, Any] = {
        "modelId": model,
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"temperature": temperature},
    }

    if tools is not None:
        payload["toolConfig"] = convert_tool_format(tools, model)

    return client.converse(**payload)

