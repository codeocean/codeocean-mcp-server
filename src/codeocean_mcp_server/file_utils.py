"""File utilities for downloading and reading files."""

import requests

# Constants
MAX_FILE_CONTENT_LENGTH = 50_000  # Maximum length of content to read
DOWNLOAD_TIMEOUT = 30


def download_and_read_file(url: str) -> str:
    """Download file from URL and return first MAX_FILE_CONTENT_LENGTH characters."""
    try:
        with requests.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True) as response:
            response.raise_for_status()
            # Read the first 'bytes_to_read' bytes of the response
            data = response.raw.read(MAX_FILE_CONTENT_LENGTH)
            # Decode the data into a string using the response's encoding
            return data.decode(response.encoding or "utf-8", errors="ignore")

    except requests.exceptions.RequestException as e:
        return f"Download error: {e}"
