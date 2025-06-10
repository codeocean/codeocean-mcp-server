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
                "search_params": {
                    "filters": [
                        {
                            "key": "tags",
                            "value": "brain"
                        }
                    ]
                }
            },
        },
    },
    # --------------------------------------------------------------
    {
        "id": "search_capsules_query_filter_sort",
        "prompt": "query for capsule with the 'DNA' in their names, return 20 capsules, "
                  "sorted by name in ascending order, and filter where there are 'aa' tag",
        "expected": {
            "name": "search_capsules",
            "input": {
                "search_params": {
                    "query": "DNA",
                    "limit": 20,
                    "sort_field": "name",
                    "sort_order": "asc",
                    "filters": [
                        {
                            "key": "tags",
                            "value": "aa"
                        }
                    ]
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
            "input": {
                "search_params": {
                    "limit": 10
                }
            }
        }
    },
    {
        "id": "search_data_assets_sorted_desc_by_name",
        "prompt": "list the data assets sorted from in descending way sorted by name",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "sort_order": "desc",
                    "sort_field": "name"
                }
            }
        }
    },
    {
        "id": "search_data_assets_sorted_by_size_asc",
        "prompt": "list data assets sorted by size in ascending order",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "sort_order": "asc",
                    "sort_field": "size"
                }
            }
        }
    },
    {
        "id": "search_data_assets_sorted_by_type",
        "prompt": "list data assets sorted by type",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "sort_field": "type"
                }
            }
        }
    },
    {
        "id": "search_data_assets_archived",
        "prompt": "list archived data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "archived": True
                }
            }
        }
    },
    {
        "id": "search_data_assets_type_dataset",
        "prompt": "list only dataset type data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "type": "dataset"
                }
            }
        }
    },
    {
        "id": "search_data_assets_type_result",
        "prompt": "find result data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "type": "result"
                }
            }
        }
    },
    {
        "id": "search_data_assets_type_model",
        "prompt": "get model data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "type": "model"
                }
            }
        }
    },
    {
        "id": "search_data_assets_origin_external",
        "prompt": "list external data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "origin": "external"
                }
            }
        }
    },
    {
        "id": "search_data_assets_origin_internal",
        "prompt": "find internal data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "origin": "internal"
                }
            }
        }
    },
    {
        "id": "search_data_assets_favorite",
        "prompt": "list my favorite data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "favorite": True
                }
            }
        }
    },
    {
        "id": "search_data_assets_ownership_mine",
        "prompt": "show my data assets",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "ownership": "mine"
                }
            }
        }
    },
    {
        "id": "search_data_assets_filter_by_tags",
        "prompt": "get data assets - filter data assets where tags = 'genomics'",
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "filters": [
                        {
                            "key": "tags",
                            "value": "genomics"
                        }
                    ]
                }
            }
        }
    },
    {
        "id": "search_data_assets_complex_query_filter_sort",
        "prompt": ("query for data asset with the 'RNA' in their names, return 20 data assets, "
                   "sorted by name in ascending order, and filter where there are 'sequencing' tag"),
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "query": "RNA",
                    "limit": 20,
                    "sort_field": "name",
                    "sort_order": "asc",
                    "filters": [
                        {
                            "key": "tags",
                            "value": "sequencing"
                        }
                    ]
                }
            }
        }
    },
    {
        "id": "search_data_assets_complex_external_ml",
        "prompt": ("find 15 external data assets that, "
                   "sorted by size descending, with 'machine learning' in description"),
        "expected": {
            "name": "search_data_assets",
            "input": {
                "search_params": {
                    "limit": 15,
                    "origin": "external",
                    "sort_field": "size",
                    "sort_order": "desc",
                    "query": "machine learning"
                }
            }
        }
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
                "data_asset_ids": [
                    {"id": "123"},
                    {"id": "456"}
                ]
            }
        }
    },
    # --------------------------------------------------------------
    # test get_capsule
    {
        "id": "get_capsule",
        "prompt": "get capsule with id: abc123 and return its details",
        "expected": {
            "name": "get_capsule",
            "input": {
                "capsule_id": "abc123"
            }
        }
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
    toolUsage = response["output"]["message"]["content"][-1]["toolUse"]
    diff = DeepDiff(expected_response, toolUsage, ignore_order=True)

    # remove any diffs about keys/items only in the ACTUAL (we only care that expected is present)
    for extra in ("dictionary_item_added", "iterable_item_added"):
        diff.pop(extra, None)

    assert not diff, f"toolUsage diverges from expected: {diff!r}"

