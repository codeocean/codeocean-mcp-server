"""End-to-end test for LOG_FORMAT, over the transport that brings a logger of its own along."""

import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SERVER_SCRIPT_PATH = str(Path(__file__).parent.parent / "src" / "codeocean_mcp_server" / "server.py")
LOG_FORMAT = "%(asctime)s server %(levelname)s [%(name)s] %(message)s"


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


def _serve_and_request(port: int) -> str:
    """Serve over streamable HTTP, make one request, and return everything the server logged."""
    env = {**os.environ, "CODEOCEAN_DOMAIN": "test-domain", "LOG_FORMAT": LOG_FORMAT}
    process = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT_PATH, "--transport", "streamable-http", "--port", str(port)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_until_listening(port)
        request = urllib.request.Request(f"http://127.0.0.1:{port}/mcp", data=b"{}")
        try:
            urllib.request.urlopen(request, timeout=30)
        except urllib.error.HTTPError:
            pass  # The request is rejected; it is logged either way, which is what is under test.
    finally:
        process.terminate()
        process.wait(timeout=30)
    return process.stdout.read()


def test_log_format_applies_to_uvicorns_own_records():
    """Uvicorn brings its own logging configuration, in whose format these records would be."""
    log = _serve_and_request(_free_port())

    timestamp = r"^[\d-]{10} [\d:,]+"
    assert re.search(rf"{timestamp} server INFO \[uvicorn\.error\] Uvicorn running", log, re.MULTILINE)
    assert re.search(
        # The status runs to the end of the line as code and phrase, which only uvicorn's own
        # access formatter puts there; the raw record carries the code alone.
        rf'{timestamp} server INFO \[uvicorn\.access\] 127\.0\.0\.1:\d+ - "POST /mcp HTTP/1.1" \d{{3}} \w+( \w+)*$',
        log,
        re.MULTILINE,
    )
