import os

from codeocean import CodeOcean
from mcp.server.fastmcp import FastMCP

from codeocean_mcp_server.tools import capsules, computations, data_assets


def main():
    """Run the MCP server."""
    domain = os.getenv("CODEOCEAN_DOMAIN")
    token = os.getenv("CODEOCEAN_TOKEN")
    if not domain or not token:
        raise ValueError(
            "Environment variables CODEOCEAN_DOMAIN and "
            "CODEOCEAN_TOKEN must be set."
        )
    agent_id = os.getenv("AGENT_ID", "AI Agent")
    client = CodeOcean(domain=domain, token=token, agent_id=agent_id)

    mcp = FastMCP(
        name="Code Ocean",
        description=(
            f"MCP server for Code Ocean: search & run capsules, "
            f"pipelines, and assets using Code Ocean domain {domain}."
        ),
    )

    capsules.add_tools(mcp, client)
    data_assets.add_tools(mcp, client)
    computations.add_tools(mcp, client)

    mcp.run()


if __name__ == "__main__":
    main()
