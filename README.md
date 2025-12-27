# Code Ocean MCP Server

Model Context Protocol (MCP) server for Code Ocean.

This MCP server provides tools to search and run capsules and pipelines, and manage data assets.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Code Ocean Platform Version Compatibility](#code-ocean-platform-version-compatibility)
- [Installation](#installation)
    - [Visual Studio Code](#visual-studio-code)
    - [Claude Desktop](#claude-desktop)
    - [Cline](#cline)
    - [Roo Code](#roo-code)
    - [Cursor](#cursor)
    - [Windsurf](#windsurf)
- [Local Testing](#local-testing)

## Prerequisites

1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python 3.10 or newer using `uv python install 3.10` (or a more recent version)
3. Generate a Code Ocean access token. Follow instructions in the [Code Ocean user guide](https://docs.codeocean.com/user-guide/code-ocean-api/authentication).

## Code Ocean Platform Version Compatibility

Each release of this Code Ocean MCP Server is tested and verified against a specific minimum version of the Code Ocean platform API.
Generally, this minimum version is the latest Code Ocean version at the time of the MCP Server release.
We recommend ensuring your MCP Server dependency is pinned to a version compatible with your Code Ocean deployment.
For details on when the minimum Code Ocean platform version changes, see the [CHANGELOG](CHANGELOG.md).

## Installation

### [Visual Studio Code](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)

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
                    "CODEOCEAN_TOKEN": "${input:codeocean-token}",
                    "AGENT_ID": "VS Code"
                }
            }
        },
    }
}
```

---

### [Claude Desktop](https://modelcontextprotocol.io/quickstart/user)

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
        "CODEOCEAN_TOKEN": "<YOUR_API_KEY>",
        "AGENT_ID": "Claude Desktop"
      }
    }
  }
}
```

---

### [Cline](https://docs.cline.bot/mcp/configuring-mcp-servers)

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
        "CODEOCEAN_TOKEN": "<YOUR_API_KEY>",
        "AGENT_ID": "Cline"
      },
      "alwaysAllow": [],       // optional: list of tools to auto-approve
      "disabled": false        // ensure it’s enabled
    }
  }
}
```
4.	Save the file. Cline will automatically detect and launch the new server, making your Code Ocean tools available in chat ￼.

--- 

### [Roo Code](https://docs.roocode.com/features/mcp/using-mcp-in-roo/)

Roo Code’s MCP support is configured globally across all workspaces via a JSON settings file or through its dedicated MCP Settings UI 

#### Via the MCP Settings UI:
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
        "CODEOCEAN_TOKEN": "<YOUR_API_KEY>",
        "AGENT_ID": "Roo Code"
      }
    }
  }
}
```
4.	Save and restart Roo Code; your Code Ocean tools will appear automatically.

#### Optional: Manually editing cline_mcp_settings.json
1.	Locate cline_mcp_settings.json (in your home directory or workspace).  ￼
2.	Insert the same "codeocean" block under "mcpServers" as above.
3.	Save and restart.

---

### [Cursor](https://docs.cursor.com/context/model-context-protocol)

Cursor stores MCP servers in a JSON file at either ~/.cursor/mcp.json (global) or {project}/.cursor/mcp.json (project-specific)  ￼.
1.	Open .cursor/mcp.json (or create it if missing).  ￼
2.	Add under "mcpServers":
```json
{
  "mcpServers": {
    "codeocean": {
      "command": "uvx",
      "args": ["codeocean-mcp-server"],
      "env": {
        "CODEOCEAN_DOMAIN": "https://codeocean.acme.com",
        "CODEOCEAN_TOKEN": "<YOUR_API_KEY>",
        "AGENT_ID": "Cursor"
      }
    }
  }
}
```
3.	Save the file. Cursor will automatically detect and launch the new server on next start.  ￼

---

### [Windsurf](https://docs.windsurf.com/windsurf/cascade/mcp)

Windsurf (Cascade) uses mcp_config.json under ~/.codeium/windsurf/ (or via the Cascade → MCP Servers UI)  ￼.
1.	Open your Windsurf Settings and navigate to Cascade → MCP Servers, then click View Raw Config to open mcp_config.json.  ￼
2.	Insert the following under "mcpServers":
```json
{
  "mcpServers": {
    "codeocean": {
      "command": "uvx",
      "args": ["codeocean-mcp-server"],
      "env": {
        "CODEOCEAN_DOMAIN": "https://codeocean.acme.com",
        "CODEOCEAN_TOKEN": "<YOUR_API_KEY>",
        "AGENT_ID": "Windsurf"
      }
    }
  }
}
```

3.	Save and restart Windsurf (or hit “Refresh” in the MCP panel).

## Local Testing

You can test the MCP server locally during development with [MCP Inspector](https://modelcontextprotocol.io/legacy/tools/inspector):

```bash
npx @modelcontextprotocol/inspector uv tool run codeocean-mcp-server
```

This will start a web server where you can:

- View available tools and resources
- Test tool calls interactively
- See server logs and responses

## Log Formatting (Optional)

The MCP server supports custom log formatting through the `LOG_FORMAT` environment variable. This allows you to control the format of log messages output by the server.
**Example Format Strings:** `"%(asctime)s %(levelname)s [%(name)s] %(message)s"`.
If `LOG_FORMAT` is not set, the server uses FastMCP's default logging configuration.
