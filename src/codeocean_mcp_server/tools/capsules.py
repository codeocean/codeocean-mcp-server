from codeocean import CodeOcean
from codeocean.capsule import (
    Capsule,
    CapsuleSearchParams,
    CapsuleSearchResults,
    Computation,
    DataAssetAttachParams,
    DataAssetAttachResults,
)
from mcp.server.fastmcp import FastMCP

from codeocean_mcp_server.models import dataclass_to_pydantic

CapsuleSearchParamsModel = dataclass_to_pydantic(CapsuleSearchParams)
CapsuleSearchResultsModel = dataclass_to_pydantic(CapsuleSearchResults)
DataAssetAttachParamsModel = dataclass_to_pydantic(DataAssetAttachParams)
DataAssetAttachResultsModel = dataclass_to_pydantic(DataAssetAttachResults)

CapsuleModel = dataclass_to_pydantic(Capsule)
ComputationModel = dataclass_to_pydantic(Computation)

ADDITIONAL_INSTRUCTIONS = {
    "search_capsules": (
        "Use only for capsule searches. "
        "Provide only the minimal required parameters (e.g. limit=10); "
        "do not include optional params"
        "like sort_by or sort_order unless requested."
    ),
    "get_capsule": (
        "Use only to fetch metadata for a known capsule ID. "
        "Do not use for searching."
    ),
    "attach_data_assets": (
        "Accepts a list of parameter objects (e.g. [{'id': '...'}]), "
        "not just a list of IDs."
    ),
}


def add_tools(mcp: FastMCP, client: CodeOcean):
    """Add capsule tools to the MCP server."""

    @mcp.tool(
        description=client.capsules.search_capsules.__doc__
        + ADDITIONAL_INSTRUCTIONS["search_capsules"]
    )
    def search_capsules(
        search_params: CapsuleSearchParamsModel,
    ) -> CapsuleSearchResultsModel:
        """Search for capsules matching specified criteria."""
        params = CapsuleSearchParams(
            **search_params.model_dump(exclude_none=True)
        )
        return client.capsules.search_capsules(params)

    @mcp.tool(
        description=client.capsules.attach_data_assets.__doc__
        + ADDITIONAL_INSTRUCTIONS["attach_data_assets"]
    )
    def attach_data_assets(
        capsule_id: str, data_asset_ids: list[DataAssetAttachParamsModel]
    ) -> list[DataAssetAttachResultsModel]:
        """Attach data assets to a capsule."""
        return client.capsules.attach_data_assets(capsule_id, data_asset_ids)

    @mcp.tool(
        description=client.capsules.get_capsule.__doc__
        + ADDITIONAL_INSTRUCTIONS["get_capsule"]
    )
    def get_capsule(capsule_id: str) -> CapsuleModel:
        """Retrieve a capsule by its ID."""
        return client.capsules.get_capsule(capsule_id)

    @mcp.tool(description=client.capsules.list_computations.__doc__)
    def list_computations(capsule_id: str) -> list[ComputationModel]:
        """List all computations for a capsule."""
        return client.capsules.list_computations(capsule_id)
