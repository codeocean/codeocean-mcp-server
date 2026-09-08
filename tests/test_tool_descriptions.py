"""Tests for the tool descriptions the server advertises.

Descriptions are composed by concatenating an SDK docstring with the server's own guidance, so these
assertions read the composed text a model actually receives rather than the source literals.
"""

import inspect

import pytest
from codeocean.capsule import Capsules
from codeocean.computation import Computations
from codeocean.custom_metadata import CustomMetadata
from codeocean.data_asset import DataAssets
from codeocean.pipeline import Pipelines
from mcp_client import get_tools

DESCRIPTIONS = {tool.name: tool.description or "" for tool in get_tools()}

# The SDK clients whose docstrings the tool descriptions are built from.
SDK_CLIENTS = (Capsules, Computations, CustomMetadata, DataAssets, Pipelines)


def _sdk_docstrings():
    """Yield (qualified name, docstring) for every documented method of the SDK clients."""
    for client in SDK_CLIENTS:
        for name, method in inspect.getmembers(client, inspect.isfunction):
            if method.__doc__ and method.__doc__.strip():
                yield f"{client.__name__}.{name}", method.__doc__


def _appended_descriptions():
    """Find every advertised description that is an SDK docstring followed by server-injected text.

    Returns a (tool, SDK method, appended remainder) triple per join, so a failure names the join
    rather than just the tool.
    """
    found = []
    for tool, description in DESCRIPTIONS.items():
        for source, docstring in _sdk_docstrings():
            body = docstring.rstrip()
            if description.startswith(body) and len(description) > len(body):
                found.append((tool, source, description[len(body) :]))
    return found


APPENDED_DESCRIPTIONS = _appended_descriptions()


def test_the_scan_finds_the_composed_descriptions():
    """Guard the scan itself: were it to match nothing, the boundary test below would be vacuous."""
    tools = {tool for tool, _, _ in APPENDED_DESCRIPTIONS}
    assert {"get_data_asset_file_urls", "wait_until_ready", "create_data_asset", "get_capsule"} <= tools


@pytest.mark.parametrize(
    ("tool", "source", "appended"),
    APPENDED_DESCRIPTIONS,
    ids=[f"{tool}-{source}" for tool, source, _ in APPENDED_DESCRIPTIONS],
)
def test_appended_guidance_is_separated_from_the_sdk_docstring(tool, source, appended):
    """Server guidance never runs into the docstring's final word.

    Some SDK docstrings end in a newline and some do not, so a join that omits its own separator is
    correct only by the grace of upstream's whitespace. Asserting on the composed text catches both
    a missing separator here and a docstring reworded upstream.
    """
    assert appended[:1].isspace(), (
        f"{tool} appends server guidance straight onto the last word of {source}'s docstring: ...{appended[:40]!r}"
    )


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
