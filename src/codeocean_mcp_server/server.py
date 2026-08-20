import argparse
import os

from codeocean import CodeOcean
from mcp.server.fastmcp import FastMCP

from codeocean_mcp_server.client import RequestScopedClient
from codeocean_mcp_server.logging_config import configure_logging
from codeocean_mcp_server.tools import (
    capsules,
    computations,
    custom_metadata,
    data_assets,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(prog="codeocean-mcp-server", description="Code Ocean MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="Transport to serve on. Over streamable-HTTP the API token is taken per request from the "
        "'Authorization: Bearer <token>' header instead of from CODEOCEAN_TOKEN.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to when serving over streamable-HTTP.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to when serving over streamable-HTTP.")
    return parser.parse_args(argv)


def main():
    """Run the MCP server."""
    configure_logging()
    args = parse_args()
    stdio = args.transport == "stdio"
    domain = os.getenv("CODEOCEAN_DOMAIN")
    token = os.getenv("CODEOCEAN_TOKEN")
    if not domain:
        raise ValueError("Environment variable CODEOCEAN_DOMAIN must be set.")
    agent_id = os.getenv("AGENT_ID", "AI Agent")

    mcp = FastMCP(
        name="Code Ocean",
        instructions=(
            f"MCP server for Code Ocean: search & run capsules, pipelines, and assets using Code Ocean domain {domain}."
        ),
        host=args.host,
        port=args.port,
        stateless_http=True,
    )

    if stdio:
        # Over stdio the process serves a single user, so the environment's client is used directly, as before.
        if not token:
            raise ValueError("Environment variable CODEOCEAN_TOKEN must be set when serving over stdio.")
        client = CodeOcean(domain=domain, token=token, agent_id=agent_id)
    else:
        client = RequestScopedClient(mcp, domain, token, agent_id)

    capsules.add_tools(mcp, client)
    data_assets.add_tools(mcp, client)
    computations.add_tools(mcp, client)
    custom_metadata.add_tools(mcp, client)

    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
