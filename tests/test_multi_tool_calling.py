from bedrock_call import call_bedrock
from deepdiff import DeepDiff
from mcp_client import get_tools
from rich import print

tools = get_tools()


agentic_prompt_chain = {
    "id": "run_capsule_and_wait",
    "prompt": "Run the capsule with ID 56473-6243-88736 and wait until it is ready, and then return the results",
    "chain": (
        (
            {"name": "run_capsule", "input": {"run_params": {"capsule_id": "56473-6243-88736"}}},
            {"computation_id": "654338-545-2232"},
        ),
        (
            {"name": "wait_until_completed", "input": {"computation_id": "654338-545-2232"}},
            {"status": "COMPLETED", "computation_id": "654338-545-2232"},
        ),
        (
            {"name": "list_computation_results", "input": {"computation_id": "654338-545-2232"}},
            {"results": {"output": "This is the output of the capsule"}},
        ),
    ),
}


def check_diff(expected_response: dict, response: dict) -> None:
    """Check that the response matches the expected response."""
    tool_usage = response["output"]["message"]["content"][-1]["toolUse"]
    diff = DeepDiff(expected_response, tool_usage, ignore_order=True)
    for extra in ("dictionary_item_added", "iterable_item_added"):
        diff.pop(extra, None)
    assert not diff, f"tool_usage diverges from expected:\n\n-----\n{diff!r}\n------"


def test_prompt_generates_correct_tool_usage_sequence(
    agentic_prompt_chain:dict = agentic_prompt_chain,
):
    """Test that the prompt generates the expected sequence of tool calls in the correct order."""
    responses = []
    prompt = ""
    for idx, step in enumerate(agentic_prompt_chain["chain"]):
        print("running step:", idx)
        if not prompt:
            prompt = agentic_prompt_chain["prompt"]
        else:
            prompt += str(responses) + "\nwhat is the next step?\n"
        response = call_bedrock(prompt=prompt, tools=tools)
        check_diff(step[0], response)
        responses.append(
            {
                "prompt": prompt,
                "call": response["output"]["message"]["content"][-1]["toolUse"],
                "response": step[1],
            }
        )
