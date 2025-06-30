# Code Ocean MCP Server

Model Context Protocol (MCP) server for Code Ocean.

This MCP server provides tools to search and run capsules and pipelines, and manage data assets.

## Prerequisites

### Installing uv
1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python 3.10 or newer using `uv python install 3.10` (or a more recent version)


### Getting code ocean's token
follow the instructions in [code ocean authentication](https://docs.codeocean.com/user-guide/code-ocean-api/authentication)


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
--- 
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

--- 
## Installing in [Cline](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)

Cline stores all of its MCP settings in a JSON file called cline_mcp_settings.json. You can edit this either through the GUI (“Configure MCP Servers” in the MCP Servers pane) or by hand:
1.	Open Cline and click the MCP Servers icon in the sidebar.
2.	In the “Installed” tab, click Configure MCP Servers → this opens your cline_mcp_settings.json.
3.	Add a "codeocean" server under the "mcpServers" key. For stdio transport:
```json
{
  "mcpServers": {
    "codeocean": {
      "command": "uvx",
      "args": ["codeocean-mcp-server"],
      "env": {
        "CODEOCEAN_DOMAIN": "https://codeocean.acme.com",
        "CODEOCEAN_TOKEN": "<YOUR_API_KEY>"
      },
      "alwaysAllow": [],       // optional: list of tools to auto-approve
      "disabled": false        // ensure it’s enabled
    }
  }
}
```
4.	Save the file. Cline will automatically detect and launch the new server, making your Code Ocean tools available in chat ￼.

[cline docs: Configuring MCP Servers](https://docs.cline.bot/mcp/configuring-mcp-servers)


--- 

## Installing in [Roo Code](https://docs.roocode.com/features/mcp/using-mcp-in-roo/)

Roo Code’s MCP support is configured globally across all workspaces via a JSON settings file or through its dedicated MCP Settings UI 

### Via the MCP Settings UI:
1.	Click the MCP icon in Roo Code’s sidebar.  ￼
2.	Select Edit MCP Settings (opens cline_mcp_settings.json).  ￼
3.	Under "mcpServers", add:

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
4.	Save and restart Roo Code; your Code Ocean tools will appear automatically.

### Optional: Manually editing cline_mcp_settings.json
1.	Locate cline_mcp_settings.json (in your home directory or workspace).  ￼
2.	Insert the same "codeocean" block under "mcpServers" as above.
3.	Save and restart.

