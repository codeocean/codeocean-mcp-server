"""Unit tests for file_utils module."""

import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from codeocean_mcp_server.file_utils import MAX_FILE_CONTENT_LENGTH, FileContent, download_and_read_file

LOG = b"".join(f"line {i:04d}\n".encode() for i in range(6000))  # 6,000 lines of 10 bytes
ERROR = b"Traceback (most recent call last):\nValueError: boom\n"


class _Handler(BaseHTTPRequestHandler):
    """Serve the requested body, honoring Range headers unless the path is /no-range.

    Under /s3, an unsatisfiable range is answered the way S3 does: no Content-Range, the size in the XML body.
    """

    files: dict[str, bytes] = {}

    def do_GET(self):  # noqa: N802
        body = self.files[self.path.removeprefix("/no-range").removeprefix("/s3")]
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
        if self.path.startswith("/no-range") or not match:
            return self._send(200, body, {})
        first, last = match.groups()
        if first:
            start, end = int(first), min(int(last or len(body) - 1), len(body) - 1)
        else:
            start, end = max(len(body) - int(last), 0), len(body) - 1
        if start >= len(body):
            if self.path.startswith("/s3"):
                error = f"<Error><Code>InvalidRange</Code><ActualObjectSize>{len(body)}</ActualObjectSize></Error>"
                return self._send(416, error.encode(), {})
            return self._send(416, b"", {"Content-Range": f"bytes */{len(body)}"})
        self._send(206, body[start : end + 1], {"Content-Range": f"bytes {start}-{end}/{len(body)}"})

    def _send(self, status, body, headers):
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
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
        "/long-line": b"x" * 1000,
        "/long-last-line": b"short\n" + b"y" * 1000 + b"\n",
    }
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


def test_offset_on_a_line_boundary_keeps_that_line(base_url):
    """A range that starts exactly at a line start does not drop that line."""
    result = download_and_read_file(f"{base_url}/log", offset=100, limit=25)
    assert result == FileContent(
        content="line 0010\nline 0011\n", offset=100, next_offset=120, total_bytes=len(LOG + ERROR)
    )


def test_offset_mid_line_starts_at_the_next_line(base_url):
    """A range that starts mid-line drops the partial first line."""
    result = download_and_read_file(f"{base_url}/log", offset=105, limit=30)
    assert result.content == "line 0011\nline 0012\n"
    assert result.offset == 110


def test_whole_small_file(base_url):
    """A file smaller than the limit is returned whole, with no next_offset."""
    assert download_and_read_file(f"{base_url}/small", offset=-1000) == FileContent(
        content="one\ntwo\nthree\n", offset=0, next_offset=None, total_bytes=14
    )


def test_offset_past_the_end_returns_empty_content(base_url):
    """An offset at or past the end of the file is not an error."""
    assert download_and_read_file(f"{base_url}/small", offset=14) == FileContent(
        content="", offset=14, next_offset=None, total_bytes=14
    )


def test_offset_past_the_end_reads_the_size_from_an_s3_error_body(base_url):
    """S3 sends no Content-Range on a 416, so the size comes from the XML error body."""
    assert download_and_read_file(f"{base_url}/s3/small", offset=100) == FileContent(
        content="", offset=100, next_offset=None, total_bytes=14
    )


def test_tail_inside_the_last_line_is_returned_as_is(base_url):
    """A tail shorter than the file's last line returns the end of that line, not nothing."""
    assert download_and_read_file(f"{base_url}/long-last-line", offset=-20) == FileContent(
        content="y" * 19 + "\n", offset=987, next_offset=None, total_bytes=1007
    )


def test_a_line_longer_than_the_limit_is_returned_as_is(base_url):
    """A single line longer than the window still makes progress."""
    result = download_and_read_file(f"{base_url}/long-line", offset=10, limit=100)
    assert result == FileContent(content="x" * 100, offset=10, next_offset=110, total_bytes=1000)


def test_server_ignoring_range_falls_back_to_the_start(base_url):
    """A 200 response is read from the start of the file."""
    result = download_and_read_file(f"{base_url}/no-range/log", offset=-100, limit=25)
    assert result == FileContent(
        content="line 0000\nline 0001\n", offset=0, next_offset=20, total_bytes=len(LOG + ERROR)
    )


def test_limit_is_capped(base_url):
    """A limit above the cap reads no more than the cap."""
    result = download_and_read_file(f"{base_url}/log", limit=10 * MAX_FILE_CONTENT_LENGTH)
    assert len(result.content.encode()) <= MAX_FILE_CONTENT_LENGTH


def test_download_error(base_url):
    """A failed download reports the error in the content."""
    result = download_and_read_file("http://127.0.0.1:1/missing")
    assert result.content.startswith("Download error:")
    assert result.next_offset is None
