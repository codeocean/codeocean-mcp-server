# test_search_capsules.py

from bedrock_call import call_bedrock
from mcp_client import get_tools

tools = get_tools()


def assert_search_capsules_used(response):
    """Assert that the search_capsules tool was used in the response."""
    tool_use = response["output"]["message"]["content"][-1]["toolUse"]
    assert tool_use["name"] == "search_capsules", "Expected tool 'search_capsules' to be used"
    assert "search_params" in tool_use["input"], f"Expected 'search_params' in tool input: {tool_use['input']}"
    return tool_use


def test_search_capsules_call_with_limit():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt =  "how can i find the first 10 capsules?", tools=tools)

    tool_use = assert_search_capsules_used(response)
    assert tool_use["input"]["search_params"]["limit"] == 10, "Expected 'limit' to be set to 10"


def test_search_capsules_call_sorted_desc():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt =  "list the capsules sorted from in descending way sorted by name", tools=tools)

    tool_use = assert_search_capsules_used(response)
    assert tool_use["input"]["search_params"]["sort_order"] == 'desc'
    assert tool_use["input"]["search_params"]["sort_field"] == 'name', "Expected 'sort_field' to be set to 'name'"



def test_search_capsules_archived():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt =  "list archived capsules", tools=tools)

    tool_use = assert_search_capsules_used(response)
    assert tool_use["input"]["search_params"]["archived"], "Expected 'archived' to be set to True"


def test_search_capsules_released():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt =  "list only released capsules", tools=tools)

    tool_use = assert_search_capsules_used(response)
    assert tool_use["input"]["search_params"]["status"] == "release", "Expected 'archived' to be set to True"


def test_search_capsules_filter():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt =  "get capsules - filter capsules where tags = 'brain'", tools=tools)

    tool_use = assert_search_capsules_used(response)
    # {'filters': [{'key': 'tags', 'value': 'brain'}]}
    assert tool_use["input"]["search_params"]["filters"]
    assert len(tool_use["input"]["search_params"]["filters"]) == 1, "Expected one filter to be applied"
    assert tool_use["input"]["search_params"]["filters"][0]["key"] == "tags"
    assert tool_use["input"]["search_params"]["filters"][0]["value"] == "brain"


def test_search_capsules_query_filter_sort():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt =  "query for capsule with the 'DNA' in their names, return 20 capsules, sorted by name in ascending order, and filter where there are 'aa' tag", tools=tools)  # noqa: E501
    tool_use = assert_search_capsules_used(response)
    # {'query': 'DNA', 'limit': 20, 'sort_field': 'name', 'sort_order': 'asc', 'filters': [{'key': 'tags', 'value': 'aa'}]}  # noqa: E501
    assert tool_use["input"]["search_params"]["query"] == "DNA", "Expected 'query' to be set to 'DNA'"
    assert tool_use["input"]["search_params"]["limit"] == 20, "Expected 'limit' to be set to 20"
    assert tool_use["input"]["search_params"]["sort_field"] == "name", "Expected 'sort_field' to be set to 'name'"
    assert tool_use["input"]["search_params"]["sort_order"] == "asc", "Expected 'sort_order' to be set to 'asc'"
    assert tool_use["input"]["search_params"]["filters"]
    assert len(tool_use["input"]["search_params"]["filters"]) == 1, "Expected one filter to be applied"
    assert tool_use["input"]["search_params"]["filters"][0]["key"] == "tags"
    assert tool_use["input"]["search_params"]["filters"][0]["value"] == "aa", "Expected filter value to be 'aa'"