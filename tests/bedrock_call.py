# bedrock_call.py

from pprint import pprint
from typing import Any, Dict, Final, List

import boto3
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL: Final = "amazon.nova-pro-v1:0"
# DEFAULT_MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"
BEDROCK_PROFILE: Final = "145023121181_Administrator"
REGION: Final = "us-east-1"

session = boto3.Session(profile_name=BEDROCK_PROFILE)
client = session.client("bedrock-runtime", region_name=REGION)


# Helper: strip unsupported JSON-Schema keys                                  #
_ALLOWED_SCHEMA_KEYS = {"type", "properties", "required", "description", "title"}


def _sanitize_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Return a shallow copy of *schema* containing only keys permitted by Bedrock's ToolInputSchema (see docs).\

    Any nested objects inside 'properties' are left untouched; only top-level keys are filtered.
    """
    return {k: v for k, v in schema.items() if k in _ALLOWED_SCHEMA_KEYS}


# Public converter                                                            #
def convert_tools_format_to_bedrock(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert MCP-style tool descriptors to the structure required by Bedrock.

    Expected input for each tool:
        {"name": str, "description": str, "parameters": dict}

    Returned list:
        [{
            "toolSpec": {
                "name": ...,
                "description": ...,
                "inputSchema": {"json": {...sanitised schema...}}
            }
        }, ...]
    """
    converted: List[Dict[str, Any]] = []
    for tool in tools:
        if not {"name", "description", "parameters"} <= tool.keys():
            raise ValueError("Each tool must have 'name', 'description', 'parameters'.")

        cleaned_schema = _sanitize_schema(tool["parameters"])

        converted.append(
            {
                "toolSpec": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "inputSchema": {"json": cleaned_schema},
                }
            }
        )
    return converted


# --------------------------------------------------------------------------- #
# Bedrock call                                                                #
# --------------------------------------------------------------------------- #
def call_bedrock(
    prompt: str,
    tools: List[Dict[str, Any]] | None = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
) -> Dict[str, Any]:
    """Send *prompt* (and optional tools) to Amazon Bedrock via the Converse API."""
    payload: Dict[str, Any] = {
        "modelId": model,
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"temperature": temperature},
    }

    if tools:
        payload["toolConfig"] = {"tools": convert_tools_format_to_bedrock(tools)}

    return client.converse(**payload)




# Quick manual test                                                           #
if __name__ == "__main__":
    reply = call_bedrock("How can I find the first 10 capsules?")
    pprint(reply["output"]["message"]["content"])
