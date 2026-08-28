import logging
import os
import sys


def configure_logging(transport: str = "stdio") -> None:
    """Configure logging based on LOG_FORMAT environment variable.

    If LOG_FORMAT is set, configures the root logger with a StreamHandler
    using the specified format string, and, for a transport uvicorn serves,
    applies the same format to uvicorn's own loggers. This must be called
    before FastMCP initialization to ensure our configuration takes
    precedence.

    If LOG_FORMAT is not set or is empty, does nothing and lets FastMCP
    configure logging with its default settings.

    Args:
        transport: The transport the server is about to serve on.

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

    if transport == "stdio":
        return

    # Serving over HTTP, uvicorn logs through its own loggers, which it gives handlers that do not
    # propagate to the root logger. It configures them from this dictionary, which FastMCP leaves
    # at its default value, so its contents have to be replaced to be reached at all. The import
    # is local because uvicorn, like in FastMCP itself, is only needed for the transports it serves.
    from uvicorn.config import LOGGING_CONFIG

    LOGGING_CONFIG["formatters"]["default"]["fmt"] = log_format
    # Access records carry the request in fields of their own rather than in the message.
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = log_format.replace(
        "%(message)s", '%(client_addr)s - "%(request_line)s" %(status_code)s'
    )
