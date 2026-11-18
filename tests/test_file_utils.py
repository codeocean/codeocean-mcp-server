"""Unit tests for file_utils module."""

import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
import requests

from codeocean_mcp_server.file_utils import MAX_FILE_CONTENT_LENGTH, FileContent, download_and_read_file

LOG = b"".join(f"line {i:04d}\n".encode() for i in range(6000))  # 6,000 lines of 10 bytes
ERROR = b"Traceback (most recent call last):\nValueError: boom\n"


class _Handler(BaseHTTPRequestHandler):
    """Serve the requested body, honoring Range headers unless the path is /no-range.

    A /no-content-range path answers 206 without the Content-Range header.
    """

    files: dict[str, bytes] = {}
    content_types: dict[str, str] = {}

    def do_GET(self):  # noqa: N802
        self.content_type = self.content_types.get(self.path, "text/plain; charset=utf-8")
        body = self.files[self.path.removeprefix("/no-range").removeprefix("/no-content-range")]
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
        if self.path.startswith("/no-range") or not match:
            return self._send(200, body, {})
        first, last = match.groups()
        if first:
            start, end = int(first), min(int(last or len(body) - 1), len(body) - 1)
        else:
            start, end = max(len(body) - int(last), 0), len(body) - 1
        if start >= len(body):
            return self._send(416, b"", {"Content-Range": f"bytes */{len(body)}"})
        headers = {"Content-Range": f"bytes {start}-{end}/{len(body)}"}
        self._send(206, body[start : end + 1], {} if self.path.startswith("/no-content-range") else headers)

    def _send(self, status, body, headers):
        self.send_response(status)
        self.send_header("Content-Type", self.content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def base_url():
    """Run a local file server for the tests."""
    _Handler.files = {
        "/log": LOG + ERROR,
        "/small": b"one\ntwo\nthree\n",
        "/long-last-line": b"short\n" + b"y" * 1000 + b"\n",
        "/long-first-line": b"x" * 150 + b"\nend\n",
        "/binary": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR",
        "/no-charset": "naïve → ✓\n".encode(),
    }
    _Handler.content_types = {"/no-charset": "text/plain"}
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


def test_reads_from_the_start_by_default(base_url):
    """A default read returns the first window, cut at a whole line, with where to continue."""
    result = download_and_read_file(f"{base_url}/log")
    assert result.offset == 0
    assert result.total_bytes == len(LOG + ERROR)
    assert result.content.startswith("line 0000\n")
    assert result.content.endswith("\n")
    assert result.next_offset == len(result.content.encode())
    assert len(result.content.encode()) <= MAX_FILE_CONTENT_LENGTH


def test_negative_offset_reads_the_tail(base_url):
    """A negative offset returns the end of the file, starting on a whole line."""
    result = download_and_read_file(f"{base_url}/log", offset=-100)
    assert result.content.endswith(ERROR.decode())
    assert result.content.startswith("line ")
    assert result.next_offset is None
    assert result.offset + len(result.content.encode()) == result.total_bytes


def test_paging_with_next_offset_reads_the_whole_file(base_url):
    """Following next_offset reads every byte once, in order."""
    content, offset = "", 0
    while offset is not None:
        result = download_and_read_file(f"{base_url}/log", offset=offset, limit=4096)
        assert result.offset == offset
        content += result.content
        offset = result.next_offset
    assert content == (LOG + ERROR).decode()


def test_offset_past_the_end_returns_empty_content(base_url):
    """An offset at or past the end of the file is not an error."""
    assert download_and_read_file(f"{base_url}/small", offset=14) == FileContent(content="", offset=14)


def test_tail_inside_the_last_line_is_returned_as_is(base_url):
    """A tail shorter than the file's last line returns the end of that line, not nothing."""
    assert download_and_read_file(f"{base_url}/long-last-line", offset=-20) == FileContent(
        content="y" * 19 + "\n", offset=987, next_offset=None, total_bytes=1007
    )


def test_paging_keeps_a_line_longer_than_the_limit(base_url):
    """Following next_offset through a line longer than one page returns the whole line."""
    content, offset = "", 0
    while offset is not None:
        result = download_and_read_file(f"{base_url}/long-first-line", offset=offset, limit=100)
        assert result.offset == offset
        content += result.content
        offset = result.next_offset
    assert content == "x" * 150 + "\nend\n"


def test_server_ignoring_range_falls_back_to_the_start(base_url):
    """A 200 response is read from the start of the file."""
    result = download_and_read_file(f"{base_url}/no-range/log", offset=-100, limit=25)
    assert result == FileContent(
        content="line 0000\nline 0001\n", offset=0, next_offset=20, total_bytes=len(LOG + ERROR)
    )


def test_missing_content_range_reads_without_a_total(base_url):
    """A 206 without Content-Range is read from the requested offset, with an unknown size."""
    assert download_and_read_file(f"{base_url}/no-content-range/small", offset=4, limit=6) == FileContent(
        content="two\n", offset=4, next_offset=8, total_bytes=None
    )


def test_limit_below_one_still_advances(base_url):
    """A zero or negative limit reads one byte instead of returning a next_offset that never moves."""
    for limit in (0, -5):
        assert download_and_read_file(f"{base_url}/small", limit=limit) == FileContent(
            content="o", offset=0, next_offset=1, total_bytes=14
        )


def test_binary_file_is_reported_not_returned(base_url):
    """A file with NUL bytes returns a short notice with its size and no next_offset."""
    result = download_and_read_file(f"{base_url}/binary")
    assert result.content.startswith("Binary file (16 bytes)")
    assert result.next_offset is None
    assert result.total_bytes == 16


def test_text_without_charset_is_read_as_utf8(base_url):
    """A text/plain response with no charset is decoded as UTF-8, not ISO-8859-1."""
    assert download_and_read_file(f"{base_url}/no-charset").content == "naïve → ✓\n"


def test_download_error_raises():
    """A failed download fails the call instead of returning the error as file content."""
    with pytest.raises(requests.RequestException):
        download_and_read_file("http://127.0.0.1:1/missing")
