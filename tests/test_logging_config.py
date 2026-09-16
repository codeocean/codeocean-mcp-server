"""End-to-end tests for LOG_LEVEL and LOG_FORMAT, over the transport that brings a logger of its own along."""

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


def _serve_and_request(**variables: str) -> str:
    """Serve over streamable HTTP with exactly these LOG_* variables set, request once, and return the log.

    Whatever LOG_LEVEL and LOG_FORMAT the test run itself has are dropped, so that only the test
    decides what the server logs.
    """
    env = {name: value for name, value in os.environ.items() if name not in ("LOG_LEVEL", "LOG_FORMAT")}
    env |= {"CODEOCEAN_DOMAIN": "test-domain", **variables}
    port = _free_port()
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
    log = _serve_and_request(LOG_FORMAT=LOG_FORMAT)

    timestamp = r"^[\d-]{10} [\d:,]+"
    assert re.search(rf"{timestamp} server INFO \[uvicorn\.error\] Uvicorn running", log, re.MULTILINE)
    assert re.search(
        # The status runs to the end of the line as code and phrase, which only uvicorn's own
        # access formatter puts there; the raw record carries the code alone.
        rf'{timestamp} server INFO \[uvicorn\.access\] 127\.0\.0\.1:\d+ - "POST /mcp HTTP/1.1" \d{{3}} \w+( \w+)*$',
        log,
        re.MULTILINE,
    )


def test_log_level_quiets_a_request_the_caller_does_not_want_logged():
    """Both loggers have to be reached: uvicorn takes its level from FastMCP, the SDK from the root."""
    log = _serve_and_request(LOG_LEVEL="WARNING", LOG_FORMAT=LOG_FORMAT)

    assert "[uvicorn.access]" not in log
    assert "[uvicorn.error]" not in log
    assert "server INFO" not in log
    # The rejected request is still warned about: the level drops the chatter, not the record
    # that says something went wrong.
    assert "server WARNING [" in log


def test_log_level_applies_without_a_log_format():
    """Without LOG_FORMAT the records are FastMCP's own, and the level has to reach those too."""
    noisy = _serve_and_request()
    quiet = _serve_and_request(LOG_LEVEL="WARNING")

    # FastMCP's rich-formatted records wrap, so match a word of each.
    assert "Uvicorn running" in noisy
    assert "streamable_http_manager" in noisy
    assert "Uvicorn running" not in quiet
    assert "streamable_http_manager" not in quiet
    assert "Invalid Content-Type" in quiet  # The rejected request's WARNING is still logged.
