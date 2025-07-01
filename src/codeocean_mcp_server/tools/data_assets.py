import os

from codeocean import CodeOcean
from codeocean.data_asset import (
    DataAsset,
    DataAssetParams,
    DataAssetSearchParams,
    DataAssetSearchResults,
    DataAssetUpdateParams,
    DownloadFileURL,
    Folder,
)
from mcp.server.fastmcp import FastMCP

from codeocean_mcp_server.file_utils import download_and_read_file
from codeocean_mcp_server.models import dataclass_to_pydantic

DataAssetModel = dataclass_to_pydantic(DataAsset)
DataAssetParamsModel = dataclass_to_pydantic(DataAssetParams)
DataAssetSearchParamsModel = dataclass_to_pydantic(DataAssetSearchParams)
DataAssetUpdateParamsModel = dataclass_to_pydantic(DataAssetUpdateParams)


def add_tools(mcp: FastMCP, client: CodeOcean):
    """Add data asset tools to the MCP server."""

    @mcp.tool(
        description=(
            str(client.data_assets.search_data_assets.__doc__)
            + "Search for data assets (external or internal). You may filter by "
            "fields such as `origin`, tags, or other criteria supported by the "
            "SDK."
        )
    )
    def search_data_assets(search_params: DataAssetSearchParamsModel) -> DataAssetSearchResults:
        """Retrieve data assets matching search criteria for datasets."""
        params = DataAssetSearchParams(**search_params.model_dump(exclude_none=True))
        return client.data_assets.search_data_assets(params)

    @mcp.tool(
        description=(
            str(client.data_assets.get_data_asset_file_download_url.__doc__)
            + "Call only when the data asset is already created and in a ready "
            "state. If the asset may not yet be ready, first use "
            "`wait_until_ready` to poll until readiness, then retrieve the "
            "download URL."
        )
    )
    def get_data_asset_file_download_url(data_asset_id: str, file_path: str) -> DownloadFileURL:
        """Get a download URL for a specific file in a data asset."""
        return client.data_assets.get_data_asset_file_download_url(data_asset_id, file_path)

    @mcp.tool(
        description=(
            "Use when you want to read the content of a file from a data asset"
        )
    )
    def download_and_read_a_file_from_data_asset(data_asset_id: str, file_path: str) -> str:
        """Download a file using the provided URL and return its content."""
        file_url = client.data_assets.get_data_asset_file_download_url(data_asset_id, file_path)
        return download_and_read_file(file_url.url)

    @mcp.tool(description=client.data_assets.list_data_asset_files.__doc__)
    def list_data_asset_files(data_asset_id: str) -> Folder:
        """List files in a data asset."""
        return client.data_assets.list_data_asset_files(data_asset_id)

    @mcp.tool(description=client.data_assets.update_metadata.__doc__)
    def update_metadata(
        data_asset_id: str,
        update_params: DataAssetUpdateParamsModel,
    ) -> DataAsset:
        """Update metadata for a specific data asset."""
        params = DataAssetUpdateParams(**update_params.model_dump(exclude_none=True))
        return client.data_assets.update_metadata(data_asset_id, params)

    @mcp.tool(
        description=(
            str(client.data_assets.wait_until_ready.__doc__)
            + "Poll until the specified data asset becomes ready before "
            "performing further operations (e.g., downloading files). You can "
            "set `polling_interval` and optional `timeout`."
        )
    )
    def wait_until_ready(
        data_asset: DataAssetModel,
        polling_interval: float = 5,
        timeout: float | None = None,
    ) -> DataAsset:
        """Wait until a data asset is ready."""
        return client.data_assets.wait_until_ready(
            DataAsset(**data_asset.model_dump(exclude_none=True)),
            polling_interval,
            timeout,
        )

    @mcp.tool(
        description=(
            str(client.data_assets.create_data_asset.__doc__)
            + f"You can link to the created data assets with the 'data_asset_id' "
            f"with the pattern: {os.getenv('CODEOCEAN_DOMAIN', 'unknown')} with /data-assets/<data_asset_id>."
        )
    )
    def create_data_asset(data_asset_params: DataAssetParamsModel) -> DataAsset:
        """Create a new data asset."""
        params = DataAssetParams(**data_asset_params.model_dump(exclude_none=True))
        return client.data_assets.create_data_asset(params)
