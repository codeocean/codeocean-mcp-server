"""Tests for the tool descriptions the server advertises.

Descriptions are composed by concatenating the SDK docstring with the server's own guidance, so
these assertions read the composed text a model actually receives rather than the source literals.
"""

from mcp_client import get_tools

DESCRIPTIONS = {tool.name: tool.description or "" for tool in get_tools()}


def test_file_urls_description_joins_the_sdk_docstring_with_a_space():
    """The appended guidance does not run into the last word of the SDK docstring."""
    assert "data asset. A draft" in DESCRIPTIONS["get_data_asset_file_urls"]


def test_file_urls_description_presents_a_draft_as_readable():
    """A draft never becomes ready, so the description must not send the model off to wait on one."""
    description = DESCRIPTIONS["get_data_asset_file_urls"]
    assert "a draft never becomes ready, so never wait on one" in description
    assert "already created and in a ready state" not in description


def test_file_urls_description_keeps_readiness_for_copy_based_paths():
    """Waiting is still the right move for an asset that is genuinely still being created."""
    description = DESCRIPTIONS["get_data_asset_file_urls"]
    assert "copy-based path (captured result, connector, import)" in description
    assert "`wait_until_ready`" in description


def test_wait_until_ready_description_rules_out_drafts():
    """The polling tool itself says a draft is not something to poll."""
    assert "Never call this on a draft" in DESCRIPTIONS["wait_until_ready"]
