import logging
import os
import sys


def log_level() -> str:
    """Return the level to log at, from the LOG_LEVEL environment variable.

    FastMCP has to be constructed with it as well: it configures uvicorn's loggers from its own level,
    which it takes as a constructor argument that wins over its FASTMCP_LOG_LEVEL environment variable.

    Environment variables:
        LOG_LEVEL: DEBUG, INFO, WARNING, ERROR or CRITICAL (optional, defaults to INFO)
    """
    return os.getenv("LOG_LEVEL", "").strip().upper() or "INFO"


def configure_logging(transport: str = "stdio") -> None:
    """Configure the root logger from the LOG_LEVEL and LOG_FORMAT environment variables.

    LOG_LEVEL sets the root logger's level. LOG_FORMAT gives the root logger a stderr handler
    with that format and, for a transport uvicorn serves, applies the same format to uvicorn's
    own loggers. With neither set, logging is left as it is, for whoever embeds the server, or
    else FastMCP with its defaults, to configure. Must be called before FastMCP is constructed.

    Args:
        transport: The transport the server is about to serve on.

    Environment variables:
        LOG_LEVEL: DEBUG, INFO, WARNING, ERROR or CRITICAL (optional, defaults to INFO)
        LOG_FORMAT: Python logging format string (optional)

    Examples:
                   - "%(asctime)s agent %(levelname)s [%(name)s] %(message)s"
                   - "%(levelname)s: %(message)s"
                   - "[%(name)s] %(message)s"

    Note:
        A malformed format string fails here, at startup. One that names a field records do not
        have fails with a ValueError when the first record is formatted instead.

    """
    log_format = os.getenv("LOG_FORMAT", "").strip()

    # The level is applied when either variable is set: a handler of our own leaves FastMCP's own
    # logging.basicConfig() with nothing to do, so the level would otherwise stay at the default.
    if log_format or "LOG_LEVEL" in os.environ:
        logging.root.setLevel(log_level())

    if not log_format:
        return

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(log_format))
    logging.root.addHandler(handler)

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
