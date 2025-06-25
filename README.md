# Code Ocean MCP Server

Model Context Protocol (MCP) server for Code Ocean.

This MCP server provides tools to search and run capsules and pipelines, and manage data assets.

## Prerequisites

1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
1. Install Python 3.10 or newer using `uv python install 3.10` (or a more recent version)

## Installation

Here's an example VS Code MCP server configuration:
```json
{
    ...
    "mcp": {
        "inputs": [
            {
            "type": "promptString",
            "id": "codeocean-token",
            "description": "Code Ocean API Key",
            "password": true
            }
        ],
        "servers": {
            "codeocean": {
                "type": "stdio",
                "command": "uvx",
                "args": ["codeocean-mcp-server"],
                "env": {
                    "CODEOCEAN_DOMAIN": "https://codeocean.acme.com",
                    "CODEOCEAN_TOKEN": "${input:codeocean-token}"
                }
            }
        },
    }
}
```
