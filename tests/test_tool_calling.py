import pytest
from bedrock_call import call_bedrock
from deepdiff import DeepDiff
from mcp_client import get_tools

tools = get_tools()

# =================================================================
# test for: "search_capsules"
test_response = [
    # --------------------------------------------------------------
    {
        "id": "search_capsule_with_limit",
        "prompt": "how can i find the first 10 capsules?",
        "expected": {
            "name": "search_capsules",
            "input": {
                "search_params": {
                    "limit": 10,
                }
            },
        },
    },
    # --------------------------------------------------------------
    {
        "id": "search_capsule_sorted_desc",
        "prompt": "list the capsules sorted from in descending way sorted by name",
        "expected": {
            "name": "search_capsules",
            "input": {
                "search_params": {
                    "sort_order": "desc",
                    "sort_field": "name",
                }
            },
        },
    },
    # --------------------------------------------------------------
    {
        "id": "search_capsules_archived",
        "prompt": "list archived capsules",
        "expected": {
            "name": "search_capsules",
            "input": {
                "search_params": {
                    "archived": True,
                }
            },
        },
    },
    # --------------------------------------------------------------
    {
        "id": "search_capsules_released",
        "prompt": "list only released capsules",
        "expected": {
            "name": "search_capsules",
            "input": {
                "search_params": {
                    "status": "release",
                }
            },
        },
    },
    # --------------------------------------------------------------
    {
        "id": "search_capsules_filter",
        "prompt": "get capsules - filter capsules where tags = 'brain'",
        "expected": {
            "name": "search_capsules",
            "input": {
                "search_params": {"filters": [{"key": "tags", "value": "brain"}]}
            },
        },
    },
    # --------------------------------------------------------------
    {
        "id": "search_capsules_query_filter_sort",
        "prompt": "query for capsule with query 'DNA' return 20 capsules, "
        "sorted by name in ascending order, and filter where there are 'aa' tag",
        "expected": {
            "name": "search_capsules",
            "input": {
                "search_params": {
                    "query": "DNA",
                    "limit": 20,
                    "sort_field": "name",
                    "sort_order": "asc",
                    "filters": [{"key": "tags", "value": "aa"}],
                }
            },
        },
    },
    # =--------------------------------------------------------------
    # Search Data Assets Tests
    {
        "id": "search_data_assets_with_limit",
        "prompt": "how can i find the first 10 data assets?",
        "expected": {
            "name": "search_data_assets",
            "input": {"search_params": {"limit": 10}},
        },
    },
    {
        "id": "search_data_assets_sorted_desc_by_name",
        "prompt": "list the data assets sorted from in descending way sorted by name",
        "expected": {
            "name": "search_data_assets",
            "input": {"search_params": {"sort_order": "desc", "sort_field": "name"}},
        },
    },
    {
        "id": "search_data_assets_sorted_by_size_asc",
        "prompt": "list data assets sorted by size in ascending order",
        "expected": {
            "name": "search_data_assets",
            "input": {"search_params": {"sort_order": "asc", "sort_field": "size"}},
        },
    },
    {
        "id": "search_data_assets_sorted_by_type",
        "prompt": "list data assets sorted by type",
        "expected": {
            "name": "search_data_assets",
            "input": {"search_params": {"sort_field": "type"}},
        },
    },
    {
        "id": "search_data_assets_archived",
        "prompt": "list archived data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {"search_params": {"archived": True}},
        },
    },
    {
        "id": "search_data_assets_type_dataset",
        "prompt": "list only dataset type data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {"search_params": {"type": "dataset"}},
        },
    },
    {
        "id": "search_data_assets_type_result",
        "prompt": "find result data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {"search_params": {"type": "result"}},
        },
    },
    {
        "id": "search_data_assets_type_model",
        "prompt": "get model data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {"search_params": {"type": "model"}},
        },
    },
    {
        "id": "search_data_assets_origin_external",
        "prompt": "list external data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {"search_params": {"origin": "external"}},
        },
    },
    {
        "id": "search_data_assets_origin_internal",
        "prompt": "find internal data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {"search_params": {"origin": "internal"}},
        },
    },
    {
        "id": "search_data_assets_favorite",
        "prompt": "list my favorite data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {"search_params": {"favorite": True}},
        },
    },
    {
        "id": "search_data_assets_ownership_mine",
        "prompt": "show data assets that are owned by me",
        "expected": {
            "name": "search_data_assets",
            "input": {"search_params": {"ownership": "created"}},
        },
    },
    {
        "id": "search_data_assets_filter_by_tags",
        "prompt": "get data assets - filter data assets where tags = 'genomics'",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {"filters": [{"key": "tags", "value": "genomics"}]}
            },
        },
    },
    {
        "id": "search_data_assets_complex_query_filter_sort",
        "prompt": (
            "query for data asset with the 'RNA' in their names, return 20 data assets, "
            "sorted by name in ascending order, and filter where there are 'sequencing' tag"
        ),
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "query": "name:RNA",
                    "limit": 20,
                    "sort_field": "name",
                    "sort_order": "asc",
                    "filters": [{"key": "tags", "value": "sequencing"}],
                }
            },
        },
    },
    {
        "id": "search_data_assets_complex_external_ml",
        "prompt": (
            "find 15 external data assets that, "
            "sorted by size descending, query for 'machine learning'"
        ),
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "limit": 15,
                    "origin": "external",
                    "sort_field": "size",
                    "sort_order": "desc",
                    "query": "machine learning",
                }
            },
        },
    },
    # --------------------------------------------------------------
    # test attach_data_assets
    {
        "id": "attach_data_assets",
        "prompt": "attach data assets with ids: 123, 456 to capsule with id: abc",
        "expected": {
            "name": "attach_data_assets",
            "input": {
                "capsule_id": "abc",
                "data_asset_ids": [{"id": "123"}, {"id": "456"}],
            },
        },
    },
    # --------------------------------------------------------------
    # test get_capsule
    {
        "id": "get_capsule",
        "prompt": "get capsule with id: abc123 and return its details",
        "expected": {"name": "get_capsule", "input": {"capsule_id": "abc123"}},
    },
    # --------------------------------------------------------------
    # test list_computations capsule id
    {
        "id": "list_computations",
        "prompt": "list all computations for capsule with id: xyz789",
        "expected": {"name": "list_computations", "input": {"capsule_id": "xyz789"}},
    },
    # --------------------------------------------------------------
    # test get_computation:
    {
        "id": "get_computation",
        "prompt": "get computation with id: comp123 and return its details",
        "expected": {"name": "get_computation", "input": {"computation_id": "comp123"}},
    },
    # --------------------------------------------------------------
    # run_capsule
    {
        "id": "run_capsule",
        "prompt": "run capsule with id: capsule123, version 2, and pass parameters: param1, param2 do not wait for the result",  # noqa: E501
        "expected": {
            "name": "run_capsule",
            "input": {
                "run_params": {
                    "capsule_id": "capsule123",
                    "version": 2,
                    "parameters": ["param1", "param2"],
                }
            },
        },
    },
    # --------------------------------------------------------------
    # run capsules with data assets attached:
    {
        "id": "run_capsule_with_data_assets",
        "prompt": "run capsule with id: capsule456, version 1, and pass parameters: paramX, paramY, "
        "attach data assets with ids: data123, data456 and do not wait for the result and mount them under /data/ with the responsive paths",  # noqa: E501
        "expected": {
            "name": "run_capsule",
            "input": {
                "run_params": {
                    "capsule_id": "capsule456",
                    "version": 1,
                    "parameters": ["paramX", "paramY"],
                    "data_assets": [
                        {"id": "data123", "mount": "/data/data123"},
                        {"id": "data456", "mount": "/data/data456"},
                    ],
                }
            },
        },
    },
    # --------------------------------------------------------------
    # run pipeline
    {
        "id": "run_pipeline",
        "prompt": "run pipeline with id: pipeline456, version 1, and pass parameters: paramA, paramB and do not wait for the result",  # noqa: E501
        "expected": {
            "name": "run_capsule",
            "input": {
                "run_params": {
                    "pipeline_id": "pipeline456",
                    "version": 1,
                    "parameters": ["paramA", "paramB"],
                }
            },
        },
    },
    # --------------------------------------------------------------
    # run pipelinewait_until_completed
    {
        "id": "wait_until_completed",
        "prompt": "wait until computation with id: comp456 is completed and return its details",
        "expected": {
            "name": "wait_until_completed",
            "input": {"computation_id": "comp456"},
        },
    },
    # --------------------------------------------------------------
    # list_computation_results
    {
        "id": "list_computation_results",
        "prompt": "list results of computation with id: comp789",
        "expected": {
            "name": "list_computation_results",
            "input": {"computation_id": "comp789"},
        },
    },
    # ==============================================================================================================
    # data assets tests
    # --------------------------------------------------------------
    # get_data_asset_file_download_url
    {
        "id": "get_data_asset_file_download_url",
        "prompt": "get download URL for file '/data/file.txt' in data asset with id: data_asset123",
        "expected": {
            "name": "get_data_asset_file_download_url",
            "input": {
                "data_asset_id": "data_asset123",
                "file_path": "/data/file.txt",
            },
        },
    },
    # ---------------------------------------------------------------
    # list_data_asset_files
    {
        "id": "list_data_asset_files",
        "prompt": "list files in data asset with id: data_asset456",
        "expected": {
            "name": "list_data_asset_files",
            "input": {"data_asset_id": "data_asset456"},
        },
    },
    # --------------------------------------------------------------
    # update_metadata
    {
        "id": "update_metadata",
        "prompt": "update metadata for data asset with id: data_asset789, set name to 'New Name' and description to 'Updated description'",  # noqa: E501
        "expected": {
            "name": "update_metadata",
            "input": {
                "data_asset_id": "data_asset789",
                "update_params": {
                    "name": "New Name",
                    "description": "Updated description",
                },
            },
        },
    },
    # --------------------------------------------------------------
    # # --------------------------------------------------------------
    # update_metadata: tags
    {
        "id": "update_metadata_tags",
        "prompt": "update metadata for data asset with id: data_asset101, set tags to ['tag1', 'tag2']",
        "expected": {
            "name": "update_metadata",
            "input": {
                "data_asset_id": "data_asset101",
                "update_params": {"tags": ["tag1", "tag2"]},
            },
        },
    },
    # --------------------------------------------------------------
    # update metadata: custom metadata
    {
        "id": "update_metadata_custom_metadata",
        "prompt": "update metadata for data asset with id: data_asset102, set custom metadata 'key1' to 'value1' and 'key2' to 'value2'",  # noqa: E501
        "expected": {
            "name": "update_metadata",
            "input": {
                "data_asset_id": "data_asset102",
                "update_params": {
                    "custom_metadata": {"key1": "value1", "key2": "value2"}
                },
            },
        },
    },
    # --------------------------------------------------------------
    # data assets: wait_until_ready:
    {
        "id": "wait_until_ready_data_asset",
        "prompt": "wait until data asset with id: data_asset103 is ready and return its details",
        "expected": {
            "name": "wait_until_ready",
            "input": {"data_asset": {"id": "data_asset103"}},
        },
    },
    # --------------------------------------------------------------
    # data assets: wait_until_ready with time out 20 seconds
    {
        "id": "wait_until_ready_data_asset_with_timeout",
        "prompt": "wait until data asset with id: data_asset104 is ready, timeout after 20 seconds",
        "expected": {
            "name": "wait_until_ready",
            "input": {
                "data_asset": {"id": "data_asset104"},
                "timeout": 20,
            },
        },
    },
]


# =================================================================
# |    Test cases for tool usage in prompts                       |
# =================================================================

test_cases = [(test["prompt"], test["expected"]) for test in test_response]
ids = [test["id"] for test in test_response]


@pytest.mark.parametrize("prompt,expected_response", test_cases, ids=ids)
def test_prompt_generating_the_right_tool_usage(prompt: str, expected_response: dict):
    """Test that the prompt generates the expected tool usage."""
    response = call_bedrock(prompt=prompt, tools=tools)
    tool_usage = response["output"]["message"]["content"][-1]["toolUse"]
    diff = DeepDiff(expected_response, tool_usage, ignore_order=True)

    # remove any diffs about keys/items only in the ACTUAL (we only care that expected is present)
    for extra in ("dictionary_item_added", "iterable_item_added"):
        diff.pop(extra, None)

    assert not diff, f"tool_usage diverges from expected: {diff!r}"
