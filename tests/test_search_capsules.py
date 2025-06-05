# test_search_capsules.py

from mcp_client import get_tools
from bedrock_call import call_bedrock


def test_call_with_tools() -> dict:
    """Test calling Bedrock with tools."""
    tools = get_tools()
    prompt = "how can i find the first 10 capsules?"
    response = call_bedrock(prompt, tools=tools)
    tool_use = response["output"]["message"]["content"][-1]["toolUse"]
    assert tool_use["name"] == "search_capsules", "Expected tool 'search_capsules' to be used"
    assert "search_params" in tool_use["input"], "Expected 'search_params' in tool input"
    print(tool_use["input"]["search_params"])
    return response


if __name__ == "__main__":
    from pprint import pprint
    response = test_call_with_tools()