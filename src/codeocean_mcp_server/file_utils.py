"""File utilities for downloading and reading files."""

import re
from typing import Optional

import requests
from pydantic import BaseModel

# Constants
MAX_FILE_CONTENT_LENGTH = 50_000  # Maximum number of bytes to read per call
DOWNLOAD_TIMEOUT = 30

READ_FILE_DESCRIPTION = (
    f" Reads up to {MAX_FILE_CONTENT_LENGTH} bytes per call: a negative `offset` reads from the end of the file "
    "(use it for logs and errors), and `next_offset` is where to continue reading (null at end of file)."
)

_CONTENT_RANGE_RE = re.compile(r"bytes (?:(\d+)-(\d+)|\*)/(\d+|\*)")
_ACTUAL_OBJECT_SIZE_RE = re.compile(rb"<ActualObjectSize>(\d+)</ActualObjectSize>")


class FileContent(BaseModel):
    """A byte range of a file, trimmed to whole lines."""

    content: str
    offset: int
    next_offset: Optional[int] = None
    total_bytes: Optional[int] = None


def _parse_content_range(header: Optional[str]) -> tuple[Optional[int], Optional[int]]:
    """Return the start byte and total size from a Content-Range header, either may be None."""
    match = _CONTENT_RANGE_RE.fullmatch((header or "").strip())
    if not match:
        return None, None
    start, _, total = match.groups()
    return (int(start) if start else None), (int(total) if total != "*" else None)


def _range_header(offset: int, limit: int) -> str:
    """Build a Range header that reads one extra byte before the window to find where its first line starts."""
    if offset < 0:
        return f"bytes=-{min(-offset, limit) + 1}"
    return f"bytes={max(offset - 1, 0)}-{offset + limit - 1}"


def _unsatisfiable_range_total(response: requests.Response) -> Optional[int]:
    """Return the file size from a 416 response: its Content-Range, or the XML error body S3 sends instead."""
    _, total = _parse_content_range(response.headers.get("Content-Range"))
    if total is None:
        match = _ACTUAL_OBJECT_SIZE_RE.search(response.raw.read(MAX_FILE_CONTENT_LENGTH))
        total = int(match.group(1)) if match else None
    return total


def download_and_read_file(url: str, offset: int = 0, limit: int = MAX_FILE_CONTENT_LENGTH) -> FileContent:
    """Read up to `limit` bytes of the file at `url`, from `offset`, or from the end when `offset` is negative.

    The range is trimmed to whole lines: a partial first line is dropped when the range doesn't start at
    the beginning of the file, and a partial last line when it doesn't reach the end. A single line longer
    than the range is returned as-is.
    """
    limit = max(1, min(limit, MAX_FILE_CONTENT_LENGTH))
    try:
        with requests.get(
            url, headers={"Range": _range_header(offset, limit)}, timeout=DOWNLOAD_TIMEOUT, stream=True
        ) as response:
            if response.status_code == 416:
                return FileContent(content="", offset=max(offset, 0), total_bytes=_unsatisfiable_range_total(response))
            response.raise_for_status()
            encoding = response.encoding or "utf-8"

            if response.status_code == 206:
                start, total = _parse_content_range(response.headers.get("Content-Range"))
                start = start or 0
                data = response.raw.read(limit + 1)
                if start > 0:
                    # The first byte is the one before the window; drop through the first newline so the
                    # content starts on a line boundary. A window inside a single line is kept as-is.
                    first_newline = data.find(b"\n")
                    drop = first_newline + 1 if 0 <= first_newline < len(data) - 1 else 1
                    data, start = data[drop:], start + drop
            else:
                # The server ignored the Range header: read from the start of the file.
                content_length = response.headers.get("Content-Length")
                total = int(content_length) if content_length and content_length.isdigit() else None
                start = 0
                data = response.raw.read(limit)
                if total is None and len(data) < limit:
                    total = len(data)

            end = start + len(data)
            at_end = total is not None and end >= total
            if not at_end and not data.endswith(b"\n"):
                last_newline = data.rfind(b"\n")
                if last_newline != -1:
                    data = data[: last_newline + 1]
                    end = start + len(data)

            return FileContent(
                content=data.decode(encoding, errors="ignore"),
                offset=start,
                next_offset=None if at_end else end,
                total_bytes=total,
            )

    except requests.exceptions.RequestException as e:
        return FileContent(content=f"Download error: {e}", offset=max(offset, 0))
