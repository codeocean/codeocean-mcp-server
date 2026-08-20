"""End-to-end tests for the streamable-HTTP transport and its per-request credentials.

A stub Code Ocean API echoes back the token it was called with, so each assertion follows a token
from the MCP request header all the way to the outgoing API call.
"""

import asyncio
import base64
import json
import os
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from mcp_client import get_tools

SERVER_SCRIPT_PATH = str(Path(__file__).parent.parent / "src" / "codeocean_mcp_server" / "server.py")


class _EchoTokenHandler(BaseHTTPRequestHandler):
    """Answer the custom metadata endpoint with the basic-auth user, which is the API token."""

    def do_GET(self):  # noqa: D102, N802
        user = base64.b64decode(self.headers["Authorization"].split(" ")[1]).decode().split(":")[0]
        body = json.dumps({"categories": [user]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # noqa: D102
        pass


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_until_listening(port: int, timeout: float = 30.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise TimeoutError(f"MCP server did not start listening on port {port}")


@pytest.fixture(scope="module")
def http_server():
    """Serve the MCP server over streamable-HTTP against a stub Code Ocean API, and yield URL and domain."""
    api = ThreadingHTTPServer(("127.0.0.1", 0), _EchoTokenHandler)
    threading.Thread(target=api.serve_forever, daemon=True).start()

    port = _free_port()
    env = {**os.environ, "CODEOCEAN_DOMAIN": f"http://127.0.0.1:{api.server_address[1]}"}
    env.pop("CODEOCEAN_TOKEN", None)
    process = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT_PATH, "--transport", "streamable-http", "--port", str(port)],
        env=env,
    )
    try:
        _wait_until_listening(port)
        yield f"http://127.0.0.1:{port}/mcp", env["CODEOCEAN_DOMAIN"]
    finally:
        process.terminate()
        process.wait(timeout=30)
        api.shutdown()


def _stdio_server(domain: str) -> StdioServerParameters:
    """Describe the same server run over stdio, against the same Code Ocean domain."""
    return StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT_PATH],
        env={"CODEOCEAN_DOMAIN": domain, "CODEOCEAN_TOKEN": "token"},
    )


async def _call_get_custom_metadata(url: str, token: str | None):
    headers = {"Authorization": f"Bearer {token}"} if token else None
    async with streamablehttp_client(url, headers=headers) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            return await session.call_tool("get_custom_metadata", {})


def test_concurrent_requests_use_their_own_token(http_server):
    """Each request acts with the token from its own authorization header."""
    url, _ = http_server

    async def both():
        return await asyncio.gather(
            _call_get_custom_metadata(url, "alice-token"),
            _call_get_custom_metadata(url, "bob-token"),
        )

    alice, bob = asyncio.run(both())
    assert alice.structuredContent["categories"] == ["alice-token"]
    assert bob.structuredContent["categories"] == ["bob-token"]


def test_request_without_credential_is_refused(http_server):
    """A request carrying no token is refused rather than served with the environment's client."""
    url, _ = http_server
    result = asyncio.run(_call_get_custom_metadata(url, None))
    assert result.isError
    assert "Missing Code Ocean API token" in result.content[0].text


def test_tool_definitions_match_stdio(http_server):
    """Serving over HTTP leaves tool names, schemas and descriptions exactly as stdio serves them."""
    url, domain = http_server

    async def list_over_http():
        async with streamablehttp_client(url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                return (await session.list_tools()).tools

    over_stdio = get_tools(_stdio_server(domain))
    assert [t.model_dump() for t in asyncio.run(list_over_http())] == [t.model_dump() for t in over_stdio]
