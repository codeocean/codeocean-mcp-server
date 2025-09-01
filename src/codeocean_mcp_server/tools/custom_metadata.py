from codeocean import CodeOcean
from codeocean.custom_metadata import CustomMetadata
from mcp.server.fastmcp import FastMCP

from codeocean_mcp_server.models import dataclass_to_pydantic

CustomMetadataModel = dataclass_to_pydantic(CustomMetadata)


def add_tools(mcp: FastMCP, client: CodeOcean):
    """Add custom_metadata tools to the MCP server."""

    @mcp.tool(description=client.custom_metadata.get_custom_metadata.__doc__)
    def get_custom_metadata() -> CustomMetadataModel:
        """Retrieve custom metadata."""
        return client.custom_metadata.get_custom_metadata()
