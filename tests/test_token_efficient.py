"""Unit tests for token_efficient module."""

from dataclasses import dataclass
from typing import Optional

from codeocean_mcp_server.token_efficient import (
    CAPSULE_COLUMNS,
    DATA_ASSET_COLUMNS,
    TAGS_TRUNCATION_MARKER,
    TRUNCATION_SUFFIX,
    CompactSearchMeta,
    extract_compact_row,
    limit_tags,
    to_compact_table,
    truncate_description,
)


class TestTruncateDescription:
    """Tests for truncate_description function."""

    def test_none_input(self):
        """None input returns None."""
        assert truncate_description(None) is None

    def test_empty_string(self):
        """Empty string input returns None."""
        assert truncate_description("") is None

    def test_whitespace_only(self):
        """Whitespace-only input returns None."""
        assert truncate_description("   ") is None

    def test_short_description(self):
        """Under 200 chars returns unchanged text."""
        text = "This is a short description."
        assert truncate_description(text) == text

    def test_exact_length(self):
        """Exactly 200 chars returns unchanged."""
        text = "a" * 200
        assert truncate_description(text) == text

    def test_whitespace_preserved_single(self):
        """Single newlines and spaces are preserved."""
        text = "Line one\nLine two"
        assert truncate_description(text) == text

    def test_whitespace_collapsed_multiple(self):
        """3+ consecutive whitespace chars are collapsed."""
        text = "Word one   Word two"  # 3 spaces
        assert truncate_description(text) == "Word one Word two"

        text_newlines = "Line one\n\n\nLine two"  # 3 newlines
        assert truncate_description(text_newlines) == "Line one Line two"

    def test_truncation_at_word_boundary(self):
        """Truncation occurs at word boundary when possible."""
        # Create text that's over 200 chars with spaces
        text = "word " * 50  # 250 chars
        result = truncate_description(text)

        assert result is not None
        assert result.endswith(TRUNCATION_SUFFIX)
        assert len(result) <= 200
        # Should end at a word boundary (not mid-word)
        without_suffix = result[: -len(TRUNCATION_SUFFIX)]
        assert without_suffix.endswith("word")

    def test_truncation_no_space(self):
        """Long string without spaces hard-cuts."""
        text = "a" * 250
        result = truncate_description(text)

        assert result is not None
        assert result.endswith(TRUNCATION_SUFFIX)
        assert len(result) == 200

    def test_truncation_suffix_present(self):
        """Over 200 chars returns text ending with truncation suffix."""
        text = "This is a long description. " * 20
        result = truncate_description(text)

        assert result is not None
        assert result.endswith(TRUNCATION_SUFFIX)

    def test_unicode_handled(self):
        """Unicode chars handled correctly."""
        text = "Hello \u4e16\u754c! " * 30  # "Hello 世界! " repeated
        result = truncate_description(text)

        assert result is not None
        # Should be valid UTF-8 string
        result.encode("utf-8")

    def test_custom_max_length(self):
        """Custom max_length is respected."""
        text = "a" * 100
        result = truncate_description(text, max_length=50)

        assert result is not None
        assert len(result) == 50
        assert result.endswith(TRUNCATION_SUFFIX)


class TestLimitTags:
    """Tests for limit_tags function."""

    def test_none_input(self):
        """None returns empty list."""
        assert limit_tags(None) == []

    def test_empty_list(self):
        """Empty list returns empty list."""
        assert limit_tags([]) == []

    def test_under_limit(self):
        """Under 10 tags returns unchanged."""
        tags = ["tag1", "tag2", "tag3"]
        result = limit_tags(tags)
        assert result == tags
        # Should be a copy, not the same object
        assert result is not tags

    def test_exact_limit(self):
        """Exactly 10 tags returns unchanged."""
        tags = [f"tag{i}" for i in range(10)]
        result = limit_tags(tags)
        assert result == tags

    def test_over_limit(self):
        """Over 10 tags returns first 9 + marker."""
        tags = [f"tag{i}" for i in range(15)]
        result = limit_tags(tags)

        assert len(result) == 10
        assert result[:9] == tags[:9]
        assert result[9] == TAGS_TRUNCATION_MARKER

    def test_custom_max_count(self):
        """Custom max_count is respected."""
        tags = [f"tag{i}" for i in range(10)]
        result = limit_tags(tags, max_count=5)

        assert len(result) == 5
        assert result[:4] == tags[:4]
        assert result[4] == TAGS_TRUNCATION_MARKER


class TestExtractCompactRow:
    """Tests for extract_compact_row function."""

    def test_dict_input_with_slug(self):
        """Dict input extracts 5 columns for capsules."""
        item = {
            "id": "cap-123",
            "name": "Test Capsule",
            "slug": "test-capsule",
            "description": "A test capsule",
            "tags": ["tag1", "tag2"],
        }
        result = extract_compact_row(item, include_slug=True)

        assert result == ["cap-123", "Test Capsule", "test-capsule", "A test capsule", ["tag1", "tag2"]]

    def test_dict_input_without_slug(self):
        """Dict input extracts 4 columns for data assets."""
        item = {
            "id": "da-123",
            "name": "Test Data Asset",
            "description": "A test data asset",
            "tags": ["tag1"],
        }
        result = extract_compact_row(item, include_slug=False)

        assert result == ["da-123", "Test Data Asset", "A test data asset", ["tag1"]]

    def test_dataclass_input(self):
        """Dataclass input extracts correctly."""

        @dataclass
        class MockCapsule:
            id: str
            name: str
            slug: str
            description: Optional[str]
            tags: Optional[list[str]]

        item = MockCapsule(
            id="cap-456",
            name="Mock Capsule",
            slug="mock-capsule",
            description="Mock description",
            tags=["a", "b"],
        )
        result = extract_compact_row(item, include_slug=True)

        assert result == ["cap-456", "Mock Capsule", "mock-capsule", "Mock description", ["a", "b"]]

    def test_missing_fields(self):
        """Missing fields return defaults, no exception."""
        item = {"id": "123"}
        result = extract_compact_row(item, include_slug=False)

        assert result[0] == "123"  # id
        assert result[1] == ""  # name - default
        assert result[2] is None  # description - None
        assert result[3] == []  # tags - empty list

    def test_truncation_applied(self):
        """Truncation is applied to description and tags."""
        item = {
            "id": "123",
            "name": "Test",
            "description": "x" * 300,  # Long description
            "tags": [f"tag{i}" for i in range(20)],  # Many tags
        }
        result = extract_compact_row(item, include_slug=False)

        # Description should be truncated
        assert result[2].endswith(TRUNCATION_SUFFIX)
        assert len(result[2]) <= 200

        # Tags should be limited with marker
        assert len(result[3]) == 10
        assert result[3][-1] == TAGS_TRUNCATION_MARKER


class TestToCompactTable:
    """Tests for to_compact_table function."""

    def test_capsule_shape(self):
        """Capsule output has correct 5-col structure."""
        items = [
            {"id": "1", "name": "One", "slug": "one", "description": "First", "tags": ["a"]},
            {"id": "2", "name": "Two", "slug": "two", "description": "Second", "tags": ["b"]},
        ]
        result = to_compact_table(items, has_more=False, next_token=None, result_type="capsule")

        assert result.cols == CAPSULE_COLUMNS
        assert len(result.rows) == 2
        assert len(result.rows[0]) == 5
        assert result.meta.result_type == "capsule"
        assert result.meta.total_returned == 2

    def test_pipeline_shape(self):
        """Pipeline output has correct 5-col structure (same as capsule)."""
        items = [
            {"id": "1", "name": "Pipeline", "slug": "pipeline", "description": "Test", "tags": []},
        ]
        result = to_compact_table(items, has_more=True, next_token="token123", result_type="pipeline")

        assert result.cols == CAPSULE_COLUMNS
        assert result.meta.result_type == "pipeline"
        assert result.meta.has_more is True
        assert result.meta.next_token == "token123"

    def test_data_asset_shape(self):
        """Data asset output has correct 4-col structure (no slug)."""
        items = [
            {"id": "da-1", "name": "Asset", "description": "Test asset", "tags": ["x"]},
        ]
        result = to_compact_table(items, has_more=False, next_token=None, result_type="data_asset")

        assert result.cols == DATA_ASSET_COLUMNS
        assert len(result.rows[0]) == 4
        assert result.meta.result_type == "data_asset"

    def test_empty_results(self):
        """Empty results list handled correctly."""
        result = to_compact_table([], has_more=False, next_token=None, result_type="capsule")

        assert result.cols == CAPSULE_COLUMNS
        assert result.rows == []
        assert result.meta.total_returned == 0

    def test_meta_populated(self):
        """Metadata is populated correctly."""
        items = [{"id": "1", "name": "Test", "slug": "test", "description": None, "tags": None}]
        result = to_compact_table(items, has_more=True, next_token="abc", result_type="capsule")

        assert isinstance(result.meta, CompactSearchMeta)
        assert result.meta.has_more is True
        assert result.meta.next_token == "abc"
        assert result.meta.total_returned == 1
        assert result.meta.result_type == "capsule"

    def test_serializable(self):
        """Result can be serialized to JSON."""
        items = [{"id": "1", "name": "Test", "slug": "test", "description": "Desc", "tags": ["t"]}]
        result = to_compact_table(items, has_more=False, next_token=None, result_type="capsule")

        # Should not raise
        json_str = result.model_dump_json()
        assert "cols" in json_str
        assert "rows" in json_str
        assert "meta" in json_str
