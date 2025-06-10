from codeocean import CodeOcean
from codeocean.data_asset import (
    DataAsset,
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


def add_tools(mcp: FastMCP, client: CodeOcean):
    """Add data asset tools to the MCP server."""

    @mcp.tool()
    def search_data_assets(
        search_params: DataAssetSearchParamsModel,
    ) -> DataAssetSearchResults:
        """Retrieve data assets that match a rich set of search criteria, when asked for data assets or datasets.

        Data assets are stored data abstractions in CodeOcean (datasets, results, models, combined assets),
        not to be confused with capsules or pipelines.

        Parameters(of `search_params`):
        ----------
        query : str | None - free-text phrase to match data asset **name**, **description**, or **tags**;
            values: any UTF-8 string

        next_token : str | None - opaque cursor from a previous call for cursor-based pagination;
                values: string returned by the API

        offset : int | None - zero-based index of the first record *when not using* `next_token`;
                values: non-negative integer

        limit : int | None - maximum number of data assets to return in this call;
                values: positive integer (1 - 1000)

        sort_field : DataAssetSortBy | None - data asset attribute used for ordering;
                values: created | type | name | size

        sort_order : SortOrder | None - must be supplied *only* when `sort_field` is set;
                values: asc | desc (ascending or descending)

        type : DataAssetType | None - filter by data asset type;
                values: dataset | result | combined | model

        ownership : Ownership | None - scope-of-visibility filter;
                values: mine | shared | created | all

        origin : values: internal | external | None - filter by origin of the data asset (external or internal data assets.

        favorite : bool | None - restrict results by "starred" flag;
                values: true | false

        archived : bool | None - include or exclude archived data assets;
                values: true | false

        filters : list[SearchFilter] | None - additional field-level predicates combined with **AND**;
            values: list of SearchFilter:
                - key: str - field name to filter on
                - value: str | float | None - single value to match
                - values: list[str | float] | None - multiple values to match
                - range: SearchFilterRange | None - inclusive range to match
                - exclude: bool | None - if true, excludes results matching this filter

        Returns
        -------
        DataAssetSearchResultsModel
            A result bundle containing the current page (`results`), a `has_more`
            flag, and a `next_token` for continued iteration.


        Notes
        -----
        - For large result sets prefer the **cursor pattern** (`next_token`) over
            `offset` + `limit`—it is more performant and resilient to concurrent
            data changes.
        - `offset` and `next_token` are *mutually exclusive*; supplying both
            triggers a validation error.
        - The helper `search_data_assets_iterator()` abstracts cursor traversal when
            you need to stream all matches.

        """
        params = DataAssetSearchParams(**search_params.model_dump(exclude_none=True))
        return client.data_assets.search_data_assets(params)

    @mcp.tool()
    def get_data_asset_file_download_url(
        data_asset_id: str,
        file_path: str | None = None,
    ) -> DownloadFileURL:
        """Get a download URL for a specific file in a data asset.

        Parameters
        ----------
        data_asset_id : str - unique identifier of the data asset;
            values: alphanumeric data asset ID from Code Ocean

        file_path : str | None - path to the specific file within the data asset;
            values: relative path within the data asset, or None for the root

        Returns
        -------
        {"url" : str}

        """
        return client.data_assets.get_data_asset_file_download_url(
            data_asset_id, file_path
        )

    @mcp.tool()
    def list_data_asset_files(data_asset_id: str) -> FolderModel:
        """List files in a data asset.

        This tool retrieves the directory structure of files within a specific data asset.
        It can be used to explore the contents of datasets, results, or other data assets.

        Parameters
        ----------
        data_asset_id : str - unique identifier of the data asset;
            values: alphanumeric data asset ID from Code Ocean

        Returns
        -------
        FolderModel
            A structured representation of the files and folders within the data asset.

        """
        return client.data_assets.list_data_asset_files(data_asset_id)

    @mcp.tool()
    def update_metadata(
        data_asset_id: str, update_params: DataAssetUpdateParamsModel
    ) -> DataAssetModel:
        """Update metadata for a specific data asset.

        Parameters
        ----------
        data_asset_id : str - unique identifier of the data asset;
            values: alphanumeric data asset ID from Code Ocean

        update_params : DataAssetUpdateParamsModel - parameters for updating the data asset metadata;
            values:
                - name: str | None - new name for the data asset
                - description: str | None - new description for the data asset
                - tags: list[str] | None - new tags to associate with the data asset
                - metadata: dict[str, Any] | None - additional metadata to update
                - custom_metadata: Optional[dict] = None - custom metadata to update

        Returns
        -------
        None

        """
        client.data_assets.update_metadata(data_asset_id, update_params)

    @mcp.tool()
    def wait_until_ready(
        data_asset: DataAssetModel,
        polling_interval: float = 5,
        timeout: float | None = None,
    ) -> DataAssetModel:
        """Wait until a data asset is ready.

        This tool blocks until the specified data asset reaches a ready state.

        Parameters
        ----------
        data_asset : DataAssetModel - the data asset to wait for;
            values: {"id": str}

        polling_interval : float - interval in seconds to poll the data asset status;
            values: positive number representing seconds between status checks

        timeout : float | None - maximum time in seconds to wait for the data asset to be ready;
            values: positive number of seconds, or None to wait indefinitely

        Returns
        -------
        DataAssetModel
            The updated data asset object once it reaches a ready state.
        """
        return client.data_assets.wait_until_ready(
            DataAsset(**data_asset.model_dump(exclude_none=True)),
            polling_interval=polling_interval,
            timeout=timeout,
        )
