import logging
import os
import sys


def configure_logging() -> None:
    """Configure logging based on LOG_FORMAT environment variable.

    If LOG_FORMAT is set, configures the root logger with a StreamHandler
    using the specified format string. This must be called before FastMCP
    initialization to ensure our configuration takes precedence.

    If LOG_FORMAT is not set or is empty, does nothing and lets FastMCP
    configure logging with its default settings.

    Environment variables:
        LOG_FORMAT: Python logging format string (optional)

    Examples:
                   - "%(asctime)s agent %(levelname)s [%(name)s] %(message)s"
                   - "%(levelname)s: %(message)s"
                   - "[%(name)s] %(message)s"

    Note:
        Invalid format strings will cause errors when log records are formatted,
        not during initialization. This typically results in ValueError, KeyError,
        or AttributeError being raised when logging occurs.

    """
    log_format = os.getenv("LOG_FORMAT", "").strip()

    # If LOG_FORMAT is not set or empty, do nothing
    if not log_format:
        return

    # Create handler for stderr (same as FastMCP default)
    handler = logging.StreamHandler(sys.stderr)

    # Create formatter with the specified format string
    # This will raise an error if the format string is invalid (fail fast)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    # Configure root logger
    # This must be done before FastMCP calls logging.basicConfig()
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)
