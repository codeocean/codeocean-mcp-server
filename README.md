# Code Ocean MCP Server

Model Context Protocol (MCP) server for Code Ocean.

This MCP server provides tools to search and run capsules and pipelines, and manage data assets.

## Prerequisites

1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
1. Install Python 3.10 or newer using `uv python install 3.10` (or a more recent version)

## Installation

## Installing in [visual studion code](https://code.visualstudio.com/)

Here's an example VS Code MCP server configuration, where VS code can ask the user for the password (token):
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

## Installing in [Claude Desktop](https://claude.ai/download)

1.	Open the `claude_desktop_config.json` file:
 - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
 - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2.	Under the top-level "mcpServers" object, add a "codeocean" entry. For a stdio transport (child-process) it looks like this:

```json
{
  "mcpServers": {
    "codeocean": {
      "command": "uvx",
      "args": ["codeocean-mcp-server"],
      "env": {
        "CODEOCEAN_DOMAIN": "https://codeocean.acme.com",
        "CODEOCEAN_TOKEN": "<YOUR_API_KEY>"
      }
    }
  }
}
```

## Installing in [Cline]()
