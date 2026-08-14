from codeocean import CodeOcean
from codeocean.capsule import (
    AppPanel,
    Capsule,
    CapsuleReleaseJob,
    CapsuleSearchParams,
    Computation,
    DataAssetAttachParams,
    DataAssetAttachResults,
)
from mcp.server.fastmcp import FastMCP

from codeocean_mcp_server.models import dataclass_to_pydantic
from codeocean_mcp_server.search import CapsuleSearchResults

AppPanelModel = dataclass_to_pydantic(AppPanel)
CapsuleSearchParamsModel = dataclass_to_pydantic(CapsuleSearchParams)
DataAssetAttachParamsModel = dataclass_to_pydantic(DataAssetAttachParams)


def add_tools(mcp: FastMCP, client: CodeOcean):
    """Add capsule tools to the MCP server."""

    @mcp.tool(description=(str(client.capsules.search_capsules.__doc__) + " " + str(CapsuleSearchResults.__doc__)))
    def search_capsules(
        search_params: CapsuleSearchParamsModel,
        include_field_names: bool = False,
    ) -> CapsuleSearchResults:
        """Search for capsules matching specified criteria."""
        params = CapsuleSearchParams(**search_params.model_dump(exclude_none=True))
        results = client.capsules.search_capsules(params)
        return CapsuleSearchResults.from_sdk_results(results, include_field_names)

    @mcp.tool(description=(str(client.pipelines.search_pipelines.__doc__) + " " + str(CapsuleSearchResults.__doc__)))
    def search_pipelines(
        search_params: CapsuleSearchParamsModel,
        include_field_names: bool = False,
    ) -> CapsuleSearchResults:
        """Search for pipelines matching specified criteria."""
        params = CapsuleSearchParams(**search_params.model_dump(exclude_none=True))
        results = client.pipelines.search_pipelines(params)
        return CapsuleSearchResults.from_sdk_results(results, include_field_names)

    @mcp.tool(
        description=(
            str(client.capsules.get_capsule.__doc__) + "Use only to fetch metadata for a known capsule ID. "
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

    @mcp.tool(
        description=(
            str(client.capsules.attach_data_assets.__doc__)
            + " Use when the capsule has no running cloud workstations. For active cloud workstation sessions"
            " use attach_computation_data_assets instead."
            " Accepts a list of parameter objects (e.g. [{'id': '...'}]), not just a list of IDs."
        )
    )
    def attach_data_assets(
        capsule_id: str,
        attach_params: list[DataAssetAttachParamsModel],
    ) -> list[DataAssetAttachResults]:
        """Attach data assets to a capsule."""
        params = [DataAssetAttachParams(**p.model_dump(exclude_none=True)) for p in attach_params]
        return client.capsules.attach_data_assets(capsule_id, params)

    @mcp.tool(
        description=(
            str(client.capsules.detach_data_assets.__doc__)
            + " Use when the capsule has no running cloud workstations. For active cloud workstation sessions"
            " use detach_computation_data_assets instead."
        )
    )
    def detach_data_assets(capsule_id: str, data_assets: list[str]) -> None:
        """Remove attached data assets from a capsule."""
        client.capsules.detach_data_assets(capsule_id, data_assets)

    @mcp.tool(description=client.capsules.get_capsule_app_panel.__doc__)
    def get_capsule_app_panel(capsule_id: str, version: int | None = None) -> AppPanelModel:
        """Retrieve the app panel for a capsule, optionally for a specific version."""
        return client.capsules.get_capsule_app_panel(capsule_id, version)

    @mcp.tool(description=str(client.capsules.release_capsule.__doc__))
    def release_capsule(capsule_id: str) -> CapsuleReleaseJob:
        """Start releasing a new version of an already-released capsule."""
        return client.capsules.release_capsule(capsule_id)

    @mcp.tool(description=str(client.pipelines.release_pipeline.__doc__))
    def release_pipeline(pipeline_id: str) -> CapsuleReleaseJob:
        """Start releasing a new version of an already-released pipeline."""
        return client.pipelines.release_pipeline(pipeline_id)

    @mcp.tool(description=str(client.capsules.get_release_job.__doc__))
    def get_capsule_release_job(capsule_id: str, job_id: str) -> CapsuleReleaseJob:
        """Get the status of a capsule release job."""
        return client.capsules.get_release_job(capsule_id, job_id)

    @mcp.tool(description=str(client.pipelines.get_release_job.__doc__))
    def get_pipeline_release_job(pipeline_id: str, job_id: str) -> CapsuleReleaseJob:
        """Get the status of a pipeline release job."""
        return client.pipelines.get_release_job(pipeline_id, job_id)

    @mcp.tool(description=str(client.capsules.wait_until_release_completed.__doc__))
    def wait_until_capsule_release_completed(capsule_id: str, job_id: str) -> CapsuleReleaseJob:
        """Wait until a capsule release job reaches a terminal state and return it."""
        job = client.capsules.get_release_job(capsule_id, job_id)
        return client.capsules.wait_until_release_completed(capsule_id, job)

    @mcp.tool(description=str(client.pipelines.wait_until_release_completed.__doc__))
    def wait_until_pipeline_release_completed(pipeline_id: str, job_id: str) -> CapsuleReleaseJob:
        """Wait until a pipeline release job reaches a terminal state and return it."""
        job = client.pipelines.get_release_job(pipeline_id, job_id)
        return client.pipelines.wait_until_release_completed(pipeline_id, job)
