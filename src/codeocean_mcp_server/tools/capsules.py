from codeocean import CodeOcean
from codeocean.capsule import CapsuleSearchParams, CapsuleSearchResults
from mcp.server.fastmcp import FastMCP

from codeocean_mcp_server.models import dataclass_to_pydantic

CapsuleSearchParamsModel = dataclass_to_pydantic(CapsuleSearchParams)
CapsuleSearchResultsModel = dataclass_to_pydantic(CapsuleSearchResults)


def add_tools(mcp: FastMCP, client: CodeOcean):
    """Add capsule tools to the MCP server."""

    @mcp.tool()
    def search_capsules(search_params: CapsuleSearchParamsModel) -> CapsuleSearchResultsModel:
        """Retrieve capsules that match a rich set of search criteria, when asked for capsules or tools.

        Capsules are a compute environment abstraction in CodeOcean, not to be confused with data asssets or pipelines.

        Parameters(of `search_params`):
        ----------
        query : str | None - free-text phrase to match capsule **name**, **description**, **tags**, or
            article title;
            values: any UTF-8 string

        next_token : str | None - opaque cursor from a previous call for cursor-based pagination;
                values: string returned by the API

        offset : int | None - zero-based index of the first record *when not using* `next_token`;
                values: non-negative integer

        limit : int | None - maximum number of capsules to return in this call;
                values: positive integer (1 - 1000)

        sort_field : CapsuleSortBy | None - capsule attribute used for ordering;
                values: created | last_accessed | name

        sort_order : SortOrder | None - must be supplied *only* when `sort_field` is set;
                values: asc | desc (ascending or descending)

        ownership : Ownership | None - scope-of-visibility filter;
                values: mine | shared | created | all

        status : CapsuleStatus | None - release-state filter;
                values: release | non_release

        favorite : bool | None - restrict results by "starred" flag;
                values: true | false

        archived : bool | None - include or exclude archived capsules;
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
        CapsuleSearchResultsModel
            A result bundle containing the current page (`results`), a `has_more`
            flag, and a `next_token` for continued iteration.


        Notes
        -----
        - For large result sets prefer the **cursor pattern** (`next_token`) over
            `offset` + `limit`—it is more performant and resilient to concurrent
            data changes.
        - `offset` and `next_token` are *mutually exclusive*; supplying both
            triggers a validation error.
        - The helper `search_capsules_iterator()` abstracts cursor traversal when
            you need to stream all matches.

        """
        params = CapsuleSearchParams(**search_params.model_dump(exclude_none=True))
        result = client.capsules.search_capsules(params)
        return CapsuleSearchResultsModel.model_validate(result)
