# test_search_data_assets.py

from bedrock_call import call_bedrock
from mcp_client import get_tools

tools = get_tools()


def assert_search_data_assets_used(response):
    """Assert that the search_data_assets tool was used in the response."""
    tool_use = response["output"]["message"]["content"][-1]["toolUse"]
    assert tool_use["name"] == "search_data_assets", "Expected tool 'search_data_assets' to be used"
    assert "search_params" in tool_use["input"], f"Expected 'search_params' in tool input: {tool_use['input']}"
    return tool_use


def test_search_data_assets_call_with_limit():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="how can i find the first 10 data assets?", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["limit"] == 10, "Expected 'limit' to be set to 10"


def test_search_data_assets_call_sorted_desc():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="list the data assets sorted from in descending way sorted by name", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["sort_order"] == 'desc'
    assert tool_use["input"]["search_params"]["sort_field"] == 'name', "Expected 'sort_field' to be set to 'name'"


def test_search_data_assets_sorted_by_size():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="list data assets sorted by size in ascending order", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["sort_order"] == 'asc'
    assert tool_use["input"]["search_params"]["sort_field"] == 'size', "Expected 'sort_field' to be set to 'size'"


def test_search_data_assets_sorted_by_type():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="list data assets sorted by type", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["sort_field"] == 'type', "Expected 'sort_field' to be set to 'type'"


def test_search_data_assets_archived():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="list archived data assets", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["archived"], "Expected 'archived' to be set to True"


def test_search_data_assets_type_dataset():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="list only dataset type data assets", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["type"] == "dataset", "Expected 'type' to be set to 'dataset'"


def test_search_data_assets_type_result():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="find result data assets", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["type"] == "result", "Expected 'type' to be set to 'result'"


def test_search_data_assets_type_model():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="get model data assets", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["type"] == "model", "Expected 'type' to be set to 'model'"


def test_search_data_assets_origin_external():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="list external data assets", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["origin"] == "external", "Expected 'origin' to be set to 'external'"


def test_search_data_assets_origin_internal():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="find internal data assets", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["origin"] == "internal", "Expected 'origin' to be set to 'internal'"


def test_search_data_assets_favorite():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="list my favorite data assets", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["favorite"], "Expected 'favorite' to be set to True"


def test_search_data_assets_ownership_mine():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="show my data assets", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["ownership"] == "mine", "Expected 'ownership' to be set to 'mine'"


def test_search_data_assets_filter():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="get data assets - filter data assets where tags = 'genomics'", tools=tools)

    tool_use = assert_search_data_assets_used(response)
    # {'filters': [{'key': 'tags', 'value': 'genomics'}]}
    assert tool_use["input"]["search_params"]["filters"]
    assert len(tool_use["input"]["search_params"]["filters"]) == 1, "Expected one filter to be applied"
    assert tool_use["input"]["search_params"]["filters"][0]["key"] == "tags"
    assert tool_use["input"]["search_params"]["filters"][0]["value"] == "genomics"


def test_search_data_assets_query_filter_sort():
    """Test calling Bedrock with tools."""
    response = call_bedrock(prompt="query for data asset with the 'RNA' in their names, return 20 data assets, sorted by name in ascending order, and filter where there are 'sequencing' tag", tools=tools)  # noqa: E501
    tool_use = assert_search_data_assets_used(response)
    # {'query': 'RNA', 'limit': 20, 'sort_field': 'name', 'sort_order': 'asc', 'filters': [{'key': 'tags', 'value': 'sequencing'}]}  # noqa: E501
    print(tool_use["input"]["search_params"])
    assert tool_use["input"]["search_params"]["query"] == "RNA", "Expected 'query' to be set to 'RNA'"
    assert tool_use["input"]["search_params"]["limit"] == 20, "Expected 'limit' to be set to 20"
    assert tool_use["input"]["search_params"]["sort_field"] == "name", "Expected 'sort_field' to be set to 'name'"
    assert tool_use["input"]["search_params"]["sort_order"] == "asc", "Expected 'sort_order' to be set to 'asc'"
    assert tool_use["input"]["search_params"]["filters"]
    assert len(tool_use["input"]["search_params"]["filters"]) == 1, "Expected one filter to be applied"
    assert tool_use["input"]["search_params"]["filters"][0]["key"] == "tags"
    assert (tool_use["input"]["search_params"]["filters"][0]["value"] == "sequencing"), \
        "Expected filter value to be 'sequencing'"


def test_search_data_assets_complex_query():
    """Test calling Bedrock with tools for complex query with multiple parameters."""
    prompt = ("find 15 dataset type data assets that are external origin, "
              "sorted by size descending, with 'machine learning' in description")
    response = call_bedrock(prompt=prompt, tools=tools)

    tool_use = assert_search_data_assets_used(response)
    assert tool_use["input"]["search_params"]["limit"] == 15, "Expected 'limit' to be set to 15"
    assert tool_use["input"]["search_params"]["type"] == "dataset", "Expected 'type' to be set to 'dataset'"
    assert (tool_use["input"]["search_params"]["origin"] == "external"), \
        "Expected 'origin' to be set to 'external'"
    assert (tool_use["input"]["search_params"]["sort_field"] == "size"), \
        "Expected 'sort_field' to be set to 'size'"
    assert (tool_use["input"]["search_params"]["sort_order"] == "desc"), \
        "Expected 'sort_order' to be set to 'desc'"
    assert (tool_use["input"]["search_params"]["query"] == "machine learning"), \
        "Expected 'query' to contain 'machine learning'"
