from codeocean import CodeOcean
from codeocean.capsule import CapsuleReleaseJob
from mcp.server.fastmcp import FastMCP


def add_tools(mcp: FastMCP, client: CodeOcean):
    """Add capsule and pipeline release tools to the MCP server."""

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
