"""File utilities for downloading and reading files."""

import requests

# Constants
MAX_FILE_CONTENT_LENGTH = 50_000  # Maximum length of content to read
DOWNLOAD_TIMEOUT = 30


def download_and_read_file(url: str) -> str:
    """Download file from URL and return first MAX_FILE_CONTENT_LENGTH characters."""
    try:
        response = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
        response.raise_for_status()

        # Read content directly from response, limiting to 5000 chars
        content = response.text[:MAX_FILE_CONTENT_LENGTH]
        return content

    except requests.exceptions.RequestException as e:
        return f"Download error: {e}"
    except UnicodeDecodeError:
        # Handle binary files by reading as bytes and decoding
        try:
            content = response.content.decode("utf-8", errors="ignore")[
                :MAX_FILE_CONTENT_LENGTH
            ]
            return content
        except Exception as e:
            return f"Encoding error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
