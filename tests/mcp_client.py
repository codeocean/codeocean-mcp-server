# mcp_client.py

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

load_dotenv()
SCRIPT = str(
    Path(__file__).parent.parent / "src" / "codeocean_mcp_server" / "server.py"
)
SERVER = StdioServerParameters(
    command=sys.executable,  # run the interpreter itself
    args=[str(SCRIPT)],
    env={
        "CODEOCEAN_DOMAIN": os.getenv("CODEOCEAN_DOMAIN"),
        "CODEOCEAN_TOKEN": os.getenv("CODEOCEAN_TOKEN"),
    },
)


def get_tools(sever=SERVER) -> list[dict]:
    """Get tools by connecting to the MCP server and listing available tools."""

    async def async_server():
        async with stdio_client(SERVER) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as client:
                await client.initialize()
                raw_tools = await client.list_tools()
                return [
                    {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema,
                    }
                    for t in raw_tools.tools
                ]

    loop = asyncio.new_event_loop()
    tools = loop.run_until_complete(async_server())
    return tools


if __name__ == "__main__":
    print(get_tools())
