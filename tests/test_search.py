"""Unit tests for search module."""

from dataclasses import dataclass
from typing import Optional

from codeocean_mcp_server.search import (
    TAGS_TRUNCATION_MARKER,
    TRUNCATION_SUFFIX,
    CapsuleSearchResults,
    DataAssetSearchResults,
    limit_tags,
    truncate_description,
)


# Mock dataclasses for SDK results (private to avoid docstring lint rules)
@dataclass
class _MockCapsule:
    id: str
    name: str
    slug: str
    description: Optional[str]
    tags: Optional[list[str]]


@dataclass
class _MockDataAsset:
    id: str
    name: str
    description: Optional[str]
    tags: Optional[list[str]]


@dataclass
class _MockCapsuleResults:
    results: list[_MockCapsule]
    has_more: bool
    next_token: Optional[str] = None


@dataclass
class _MockDataAssetResults:
    results: list[_MockDataAsset]
    has_more: bool
    next_token: Optional[str] = None


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


class TestCapsuleSearchResults:
    """Tests for CapsuleSearchResults model."""

    def test_from_sdk_results(self):
        """from_sdk_results converts SDK results correctly."""
        capsules = [
            _MockCapsule(id="1", name="Capsule One", slug="capsule-one", description="First", tags=["a", "b"]),
            _MockCapsule(id="2", name="Capsule Two", slug="capsule-two", description=None, tags=None),
        ]
        sdk_results = _MockCapsuleResults(results=capsules, has_more=True, next_token="token123")

        result = CapsuleSearchResults.from_sdk_results(sdk_results, include_field_names=False)

        assert len(result.items) == 2
        assert result.items[0].id == "1"
        assert result.items[0].n == "Capsule One"
        assert result.items[0].s == "capsule-one"
        assert result.items[0].d == "First"
        assert result.items[0].t == ["a", "b"]
        assert result.items[1].d is None
        assert result.items[1].t == []
        assert result.has_more is True
        assert result.next_token == "token123"
        assert result.item_count == 2
        assert result.field_names is None

    def test_from_sdk_results_with_field_names(self):
        """from_sdk_results includes field_names when requested."""
        sdk_results = _MockCapsuleResults(
            results=[_MockCapsule(id="1", name="Test", slug="test", description=None, tags=None)],
            has_more=False,
        )

        result = CapsuleSearchResults.from_sdk_results(sdk_results, include_field_names=True)

        assert result.field_names == CapsuleSearchResults.FIELD_NAMES

    def test_serializable(self):
        """Result can be serialized to JSON."""
        sdk_results = _MockCapsuleResults(
            results=[_MockCapsule(id="1", name="Test", slug="test", description="Desc", tags=["t"])],
            has_more=False,
        )

        result = CapsuleSearchResults.from_sdk_results(sdk_results)
        json_str = result.model_dump_json()

        assert "items" in json_str
        assert "has_more" in json_str
        assert "item_count" in json_str


class TestDataAssetSearchResults:
    """Tests for DataAssetSearchResults model."""

    def test_from_sdk_results(self):
        """from_sdk_results converts SDK results correctly."""
        assets = [
            _MockDataAsset(id="da-1", name="Asset One", description="First asset", tags=["x"]),
            _MockDataAsset(id="da-2", name="Asset Two", description=None, tags=None),
        ]
        sdk_results = _MockDataAssetResults(results=assets, has_more=False, next_token=None)

        result = DataAssetSearchResults.from_sdk_results(sdk_results, include_field_names=False)

        assert len(result.items) == 2
        assert result.items[0].id == "da-1"
        assert result.items[0].n == "Asset One"
        assert result.items[0].d == "First asset"
        assert result.items[0].t == ["x"]
        assert result.items[1].d is None
        assert result.items[1].t == []
        assert result.has_more is False
        assert result.next_token is None
        assert result.item_count == 2
        assert result.field_names is None

    def test_truncation_applied(self):
        """Long descriptions and many tags are truncated."""
        asset = _MockDataAsset(
            id="da-1",
            name="Test",
            description="x" * 300,  # Long description
            tags=[f"tag{i}" for i in range(20)],  # Many tags
        )
        sdk_results = _MockDataAssetResults(results=[asset], has_more=False)

        result = DataAssetSearchResults.from_sdk_results(sdk_results)

        # Description should be truncated
        assert result.items[0].d is not None
        assert result.items[0].d.endswith(TRUNCATION_SUFFIX)
        assert len(result.items[0].d) <= 200

        # Tags should be limited with marker
        assert len(result.items[0].t) == 10
        assert result.items[0].t[-1] == TAGS_TRUNCATION_MARKER
