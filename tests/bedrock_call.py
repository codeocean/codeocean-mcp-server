# bedrock_call.py
import os
from typing import Any, Dict, List

import boto3
from bedrock_tools_converter import convert_tool_format

BEDROCK_MODEL = os.getenv("BEDROCK_MODEL") or "amazon.nova-pro-v1:0"

_client = None


def _get_client():
    """Lazily initialize the Bedrock client."""
    global _client
    if _client is None:
        _client = boto3.client("bedrock-runtime")
    return _client


def call_bedrock(
    prompt: str,
    tools: List[Dict[str, Any]] | None = None,
    model: str = BEDROCK_MODEL,
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

    return _get_client().converse(**payload)
