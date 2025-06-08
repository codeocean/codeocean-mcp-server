from bedrock_call import call_bedrock
from mcp_client import get_tools

tools = get_tools()


def assert_search_capsules_used(response):
    """Assert that the run_capsule_and_return_result tool was used in the response."""
    tool_use = response["output"]["message"]["content"][-1]["toolUse"]
    assert tool_use["name"] == "run_capsule_and_return_result", "Expected tool 'run_capsule_and_return_result' to be used"
    assert "run_params" in tool_use["input"], f"Expected 'run_params' in tool input: {tool_use['input']}"
    return tool_use


def test_run_capsule_and_get_results_with_capsule_id():
    """Test running a capsule and getting results using a capsule ID."""
    response = call_bedrock(
        "Run the capsule with ID '12345-abhgc-ddssdd' and return the results.",
        tools=tools,
    )
    tool_use = assert_search_capsules_used(response)
    print(tool_use["input"]["run_params"])
    assert tool_use["input"]["run_params"]["capsule_id"] == "12345-abhgc-ddssdd", "Expected capsule_id to be '12345'"

