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
DataAssetAttachParamsModel = dataclass_to_pydantic(DataAssetAttachParams)


def add_tools(mcp: FastMCP, client: CodeOcean):
    """Add capsule tools to the MCP server."""

    @mcp.tool(
        description=(
            str(client.capsules.search_capsules.__doc__)
            + "Use only for capsule searches. "
            "Provide only the minimal required parameters (e.g. limit=10); "
            "do not include optional params "
            "like sort_by or sort_order unless requested."
        )
    )
    def search_capsules(search_params: CapsuleSearchParamsModel) -> CapsuleSearchResults:
        """Search for capsules matching specified criteria."""
        params = CapsuleSearchParams(**search_params.model_dump(exclude_none=True))
        return client.capsules.search_capsules(params)

    @mcp.tool(
        description=(
            str(client.capsules.attach_data_assets.__doc__)
            + "Accepts a list of parameter objects (e.g. [{'id': '...'}]), "
            "not just a list of IDs."
        )
    )
    def attach_data_assets(
        capsule_id: str,
        attach_params: list[DataAssetAttachParamsModel],
    ) -> list[DataAssetAttachResults]:
        """Attach data assets to a capsule."""
        params = [
            DataAssetAttachParams(**p.model_dump(exclude_none=True))
            for p in attach_params
        ]
        return client.capsules.attach_data_assets(capsule_id, params)

    @mcp.tool(
        description=(
            str(client.capsules.get_capsule.__doc__)
            + "Use only to fetch metadata for a known capsule ID. "
            "Do not use for searching."
        )
    )
    def get_capsule(capsule_id: str) -> Capsule:
        """Retrieve a capsule by its ID."""
        return client.capsules.get_capsule(capsule_id)

    @mcp.tool(description=client.capsules.list_computations.__doc__)
    def list_computations(capsule_id: str) -> list[Computation]:
        """List all computations for a capsule."""
        return client.capsules.list_computations(capsule_id)
