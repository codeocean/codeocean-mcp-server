from codeocean import CodeOcean
from codeocean.data_asset import (
    DataAsset,
    DataAssetAttachParams,
    DataAssetParams,
    DataAssetSearchParams,
    DataAssetSearchResults,
    DataAssetUpdateParams,
    DownloadFileURL,
    Folder,
)
from mcp.server.fastmcp import FastMCP

from codeocean_mcp_server.models import dataclass_to_pydantic

DataAssetSearchParamsModel = dataclass_to_pydantic(DataAssetSearchParams)
DataAssetSearchResultsModel = dataclass_to_pydantic(DataAssetSearchResults)
FolderModel = dataclass_to_pydantic(Folder)
DataAssetUpdateParamsModel = (dataclass_to_pydantic(DataAssetUpdateParams),)
DataAssetModel = dataclass_to_pydantic(DataAsset)
DataAssetParamsModel = dataclass_to_pydantic(DataAssetParams)
DataAssetAttachParamsModel = dataclass_to_pydantic(DataAssetAttachParams)


ADDITIONAL_INSTRUCTIONS = {
    "get_data_asset_file_download_url" : """
Don't call when a wait is required! - only used if you know that the data assets is already created.
Otherwise, use the `wait_until_ready` tool to ensure the data asset is ready before attempting to download files.
""",
"wait_until_ready": """
Use this tool when asked to wait for a data assets to be ready.
""",
"search_data_assets": """"
 Notes:search for external and internal data assets (filterd by the 'origin' field).
"""
}

def add_tools(mcp: FastMCP, client: CodeOcean):
    """Add data asset tools to the MCP server."""

    @mcp.tool(description=client.data_assets.search_data_assets.__doc__ + ADDITIONAL_INSTRUCTIONS["search_data_assets"])
    def search_data_assets(
        search_params: DataAssetSearchParamsModel,
    ) -> DataAssetSearchResults:
        """Retrieve data assets that match a rich set of search criteria, when asked for data assets or datasets."""
        params = DataAssetSearchParams(**search_params.model_dump(exclude_none=True))
        return client.data_assets.search_data_assets(params)


    @mcp.tool(description=client.data_assets.get_data_asset_file_download_url.__doc__ + ADDITIONAL_INSTRUCTIONS["get_data_asset_file_download_url"])  # noqa: E501
    def get_data_asset_file_download_url(
        data_asset_id: str,
        file_path: str | None = None,
    ) -> DownloadFileURL:
        """Get a download URL for a specific file in a data asset."""
        return client.data_assets.get_data_asset_file_download_url(
            data_asset_id, file_path
        )


    @mcp.tool(description = client.data_assets.list_data_asset_files.__doc__)
    def list_data_asset_files(data_asset_id: str) -> FolderModel:
        """List files in a data asset."""
        return client.data_assets.list_data_asset_files(data_asset_id)


    @mcp.tool(description=client.data_assets.update_metadata.__doc__)
    def update_metadata(
        data_asset_id: str, update_params: DataAssetUpdateParamsModel
    ) -> DataAssetModel:
        """Update metadata for a specific data asset."""
        client.data_assets.update_metadata(data_asset_id, update_params)


    @mcp.tool(description=client.data_assets.wait_until_ready.__doc__ + ADDITIONAL_INSTRUCTIONS["wait_until_ready"])
    def wait_until_ready(
        data_asset: DataAssetModel,
        polling_interval: float = 5,
        timeout: float | None = None,
    ) -> DataAssetModel:
        """Wait until a data asset is ready."""
        return client.data_assets.wait_until_ready(
            DataAsset(**data_asset.model_dump(exclude_none=True)),
            polling_interval=polling_interval,
            timeout=timeout,
        )


    @mcp.tool(description=client.data_assets.create_data_asset.__doc__)
    def create_data_asset(data_asset_params: DataAssetParamsModel) -> DataAssetModel:
        """Create a new data asset."""
        return client.data_assets.create_data_asset(
            DataAsset(**data_asset_params.model_dump(exclude_none=True))
        )
