"""Pytest configuration for codeocean-mcp-server tests."""

import pytest


def pytest_addoption(parser):
    """Add --integration flag to pytest."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests (requires AWS/Bedrock setup)",
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless --integration flag is passed."""
    if config.getoption("--integration"):
        return
    skip_integration = pytest.mark.skip(reason="need --integration flag to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
