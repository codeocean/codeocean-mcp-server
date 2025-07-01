# bedrock_call.py

import copy
import re
from typing import Any, Dict, List

from jsonschema import Draft202012Validator
from mcp.types import Tool

# Bedrock naming rules: 1–64 chars, letters/numbers/underscore/hyphen only
_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")




def prune_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively prune forbidden keys from a schema."""
    forbidden_keys = {"anyOf", "$schema", "$ref"}
    conversion = {"$defs": "description"}
    pruned = copy.deepcopy(schema)

    def _prune(node: Any):
        if isinstance(node, dict):
            for key in list(node.keys()):
                if key in forbidden_keys:
                    del node[key]
                elif key in conversion:
                    node[conversion[key]] = str(node.pop(key))
                else:
                    _prune(node[key])
        elif isinstance(node, list):
            for item in node:
                _prune(item)

    _prune(pruned)
    return pruned


def _sanitize_name(name: str) -> str:
    # Replace invalid chars with underscore and trim length
    clean = re.sub(r"[^A-Za-z0-9_-]", "_", name)
    return clean[:64]


def validate_schema(schema: Dict[str, Any]) -> None:
    """Raise if schema is not valid Draft 2020-12."""
    Draft202012Validator.check_schema(schema)


def convert_tool_format(
    tools: List[Tool], model: str
) -> Dict[str, List[Dict[str, Any]]]:
    """Convert MCP tools into a Bedrock Draft 2020-12-compliant toolConfig."""
    # For other models, we need to convert tools to the Bedrock format
    converted = []
    for tool in tools:
        # 1. Sanitize and validate name
        name = _sanitize_name(tool.name)
        # 2. Build full schema including meta-schema pointer
        full_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            **tool.inputSchema,  # Preserve $defs, anyOf, etc.
        }
        # 3. Validate locally
        validate_schema(full_schema)
        # 4. Assemble Bedrock toolSpec
        converted.append(
            {
                "toolSpec": {
                    "name": name,
                    "description": tool.description or "",
                    "inputSchema": {"json": full_schema},
                }
            }
        )

    if "amazon.nova" in model:
        converted = [prune_schema(item) for item in converted]

    return {"tools": converted}
