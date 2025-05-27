import os

from codeocean import CodeOcean
from mcp.server.fastmcp import FastMCP

from codeocean_mcp_server.tools import capsules, data_assets


def main():
    """Run the MCP server."""
    domain = os.getenv("CODEOCEAN_DOMAIN")
    token = os.getenv("CODEOCEAN_TOKEN")
    if not domain or not token:
        raise ValueError(
            "Environment variables CODEOCEAN_DOMAIN and CODEOCEAN_TOKEN must be set."
        )
    client = CodeOcean(domain=domain, token=token)

    mcp = FastMCP(
        name="Code Ocean",
        description="MCP server for Code Ocean: search & run capsules, pipelines, and assets.",
    )

    capsules.add_tools(mcp, client)
    data_assets.add_tools(mcp, client)

    mcp.run()


if __name__ == "__main__":
    main()
