# bedrock_call.py

import re
from typing import Any, Dict, List

from jsonschema import Draft202012Validator
from mcp.types import Tool

# Bedrock naming rules: 1–64 chars, letters/numbers/underscore/hyphen only
_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

def _sanitize_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Return a shallow copy of *schema* containing only keys permitted by Bedrock's ToolInputSchema (see docs)."""
    _ALLOWED_SCHEMA_KEYS = {"type", "properties", "required", "description", "title"}
    return {k: v for k, v in schema.items() if k in _ALLOWED_SCHEMA_KEYS}


def convert_tool_format_nova(tools: list[Tool]) -> list[str, Any]:
    """Convert tools into the format required for the Bedrock API."""
    converted_tools = []

    for tool in tools:
        converted_tool = {
            "toolSpec": {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": {"json": _sanitize_schema(tool.inputSchema)},
            }
        }
        converted_tools.append(converted_tool)

    return {"tools": converted_tools}

def _sanitize_name(name: str) -> str:
    # Replace invalid chars with underscore and trim length
    clean = re.sub(r"[^A-Za-z0-9_-]", "_", name)
    return clean[:64]


def validate_schema(schema: Dict[str, Any]) -> None:
    """Raise if schema is not valid Draft 2020-12."""
    Draft202012Validator.check_schema(schema)


def convert_tool_format(tools: List[Tool], model:str) -> Dict[str, List[Dict[str, Any]]]:
    """Convert MCP tools into a Bedrock Draft 2020-12-compliant toolConfig."""
    if "amazon.nova" in model:
        return convert_tool_format_nova(tools)

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

    return {"tools": converted}
