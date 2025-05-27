from codeocean import CodeOcean
from codeocean.capsule import CapsuleSearchParams, CapsuleSearchResults
from mcp.server.fastmcp import FastMCP

from codeocean_mcp_server.models import dataclass_to_pydantic

CapsuleSearchParamsModel = dataclass_to_pydantic(CapsuleSearchParams)
CapsuleSearchResultsModel = dataclass_to_pydantic(CapsuleSearchResults)


def add_tools(mcp: FastMCP, client: CodeOcean):
    """Add capsule tools to the MCP server."""

    @mcp.tool()
    def search_capsules(search_params: CapsuleSearchParamsModel) -> CapsuleSearchResults:
        """Search for CodeOcean capsules using full-text, paging, sorting, ownership and other filters."""
        params = CapsuleSearchParams(**search_params.model_dump(exclude_none=True))
        return client.capsules.search_capsules(params)

