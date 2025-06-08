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

        origin : DataAssetSearchOrigin | None - filter by origin of the data asset;
                values: internal | external

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

