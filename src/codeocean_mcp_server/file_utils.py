"""File utilities for downloading and reading files."""

import codecs
from typing import Optional

import requests
from pydantic import BaseModel

# Constants
MAX_FILE_CONTENT_LENGTH = 50_000  # Maximum number of bytes to read per call
DOWNLOAD_TIMEOUT = 30


class FileContent(BaseModel):
    """Reads up to 50,000 bytes per call, trimmed to whole lines.

    A negative `offset` reads from the end of the file (use it for logs and errors).
    `next_offset` is where to continue reading (null at end of file).
    """

    content: str
    offset: int
    next_offset: Optional[int] = None
    total_bytes: Optional[int] = None


def download_and_read_file(url: str, offset: int = 0, limit: int = MAX_FILE_CONTENT_LENGTH) -> FileContent:
    """Read up to `limit` bytes of the file at `url`, from `offset`, or from the end when `offset` is negative.

    A tail is trimmed to start on a whole line; a non-negative offset starts exactly where asked, so paging
    with `next_offset` loses nothing. A partial last line is dropped when the range doesn't reach the end of
    the file. A single line longer than the range is returned as-is.
    """
    limit = min(limit, MAX_FILE_CONTENT_LENGTH)
    byte_range = f"bytes=-{min(-offset, limit)}" if offset < 0 else f"bytes={offset}-{offset + limit - 1}"
    try:
        with requests.get(url, headers={"Range": byte_range}, timeout=DOWNLOAD_TIMEOUT, stream=True) as response:
            if response.status_code == 416:
                return FileContent(content="", offset=max(offset, 0))
            response.raise_for_status()

            if response.status_code == 206:
                span, total = response.headers["Content-Range"].split("/")
                start, total = int(span.split()[1].split("-")[0]), int(total)
            else:  # server ignored Range
                start, total = 0, int(response.headers["Content-Length"])
            data = response.raw.read(limit)

            # A tail starts after its first newline; a tail inside the last line is kept as-is.
            first_newline = data.find(b"\n", 0, len(data) - 1)
            if offset < 0 and start > 0 and first_newline != -1:
                data, start = data[first_newline + 1 :], start + first_newline + 1

            at_end = start + len(data) >= total
            if not at_end and not data.endswith(b"\n") and b"\n" in data:
                data = data[: data.rfind(b"\n") + 1]

            # A character cut off at the end of the range stays unread for the next page.
            decoder = codecs.getincrementaldecoder(response.encoding or "utf-8")(errors="ignore")
            content = decoder.decode(data, final=at_end)
            end = start + len(data) - len(decoder.getstate()[0])

            return FileContent(content=content, offset=start, next_offset=None if at_end else end, total_bytes=total)

    except requests.exceptions.RequestException as e:
        return FileContent(content=f"Download error: {e}", offset=max(offset, 0))
