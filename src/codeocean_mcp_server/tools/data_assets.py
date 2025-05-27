from codeocean import CodeOcean
from codeocean.data_asset import DataAssetSearchParams, DataAssetSearchResults
from mcp.server.fastmcp import FastMCP

from codeocean_mcp_server.models import dataclass_to_pydantic

DataAssetSearchParamsModel = dataclass_to_pydantic(DataAssetSearchParams)
DataAssetSearchResultsModel = dataclass_to_pydantic(DataAssetSearchResults)


def add_tools(mcp: FastMCP, client: CodeOcean):
    """Add data asset tools to the MCP server."""

    @mcp.tool()
    def search_data_assets(search_params: DataAssetSearchParamsModel) -> DataAssetSearchResults:
        """Search for Code Ocean data assets using full-text, paging, sorting, ownership and other filters."""
        params = DataAssetSearchParams(**search_params.model_dump(exclude_none=True))
        return client.data_assets.search_data_assets(params)

