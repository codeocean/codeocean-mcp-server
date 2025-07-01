# mcp_client.py

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

SERVER_SCRIPT_PATH = str(Path(__file__).parent.parent / "src" / "codeocean_mcp_server" / "server.py")
SERVER = StdioServerParameters(
    command=sys.executable,
    args=[str(SERVER_SCRIPT_PATH)],
    env={
        "CODEOCEAN_DOMAIN": "domain",
        "CODEOCEAN_TOKEN": "token",
    },
)


def get_tools(server=SERVER) -> list[dict]:
    """Get tools by connecting to the MCP server and listing available tools."""

    async def async_server():
        async with stdio_client(server) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as client:
                await client.initialize()
                raw_tools = await client.list_tools()
                return raw_tools.tools

    loop = asyncio.new_event_loop()
    return loop.run_until_complete(async_server())
