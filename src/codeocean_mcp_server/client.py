"""Per-request Code Ocean client resolution for the streamable-HTTP transport."""

from functools import lru_cache

from codeocean import CodeOcean
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request


@lru_cache(maxsize=32)
def _cached_client(domain: str, token: str, agent_id: str | None) -> CodeOcean:
    """Return a client for the given credentials, reusing its HTTP connection pool across requests."""
    return CodeOcean(domain=domain, token=token, agent_id=agent_id)


def _bearer_token(request: Request) -> str | None:
    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    return token.strip() or None if scheme.lower() == "bearer" else None


class RequestScopedClient:
    """A `CodeOcean` stand-in that resolves to the calling request's own client on every attribute access.

    Tools reach the SDK as `client.<sub_client>.<method>(...)`, evaluated when the tool runs, so wrapping
    the client is enough to give each request its own credentials without touching the tools themselves.

    Outside a request — tool registration, where descriptions are read from SDK docstrings — attribute
    access resolves to `placeholder`, which issues no network call.
    """

    def __init__(self, mcp: FastMCP, domain: str, agent_id: str | None, placeholder: CodeOcean):
        """Wrap the credentials that are fixed for the process, around the token that varies per request."""
        self._mcp = mcp
        self._domain = domain
        self._agent_id = agent_id
        self._placeholder = placeholder

    def __getattr__(self, name: str):
        """Delegate to the calling request's client."""
        return getattr(self._resolve(), name)

    def _resolve(self) -> CodeOcean:
        try:
            request = self._mcp.get_context().request_context.request
        except ValueError:
            return self._placeholder
        token = _bearer_token(request) if request is not None else None
        if not token:
            raise ValueError("Missing Code Ocean API token: send it as an 'Authorization: Bearer <token>' header.")
        return _cached_client(self._domain, token, self._agent_id)
