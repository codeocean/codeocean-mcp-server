import re
from typing import Any, ClassVar, Optional

from pydantic import BaseModel

# Constants
MAX_DESCRIPTION_LENGTH = 200
MAX_TAGS_COUNT = 10
TRUNCATION_SUFFIX = "...(more)"
TAGS_TRUNCATION_MARKER = "..more.."


def truncate_description(description: Optional[str], max_length: int = MAX_DESCRIPTION_LENGTH) -> Optional[str]:
    """Truncate description with word-boundary-aware cutting."""
    if not description:
        return None

    # Light whitespace normalization: collapse 3+ consecutive whitespace to single space.
    normalized = re.sub(r"\s{3,}", " ", description).strip()
    if not normalized:
        return None

    if len(normalized) <= max_length:
        return normalized

    truncate_at = max_length - len(TRUNCATION_SUFFIX)
    if truncate_at <= 0:
        return TRUNCATION_SUFFIX[:max_length]

    last_space = normalized.rfind(" ", 0, truncate_at)
    cut_at = last_space if last_space > max_length // 2 else truncate_at
    return normalized[:cut_at].rstrip() + TRUNCATION_SUFFIX


def limit_tags(tags: Optional[list[str]], max_count: int = MAX_TAGS_COUNT) -> list[str]:
    """Limit tags to maximum count with truncation marker."""
    if not tags:
        return []

    if len(tags) <= max_count:
        return list(tags)

    return list(tags[: max_count - 1]) + [TAGS_TRUNCATION_MARKER]


class CompactCapsuleItem(BaseModel):
    """Compact capsule/pipeline item (id kept, other fields shortened)."""

    id: str
    n: str
    s: str
    d: Optional[str] = None
    t: list[str]


class CompactDataAssetItem(BaseModel):
    """Compact data asset item (id kept, other fields shortened)."""

    id: str
    n: str
    d: Optional[str] = None
    t: list[str]


class SearchMeta(BaseModel):
    """Base model providing search metadata fields."""

    has_more: bool
    next_token: Optional[str] = None
    item_count: int
    field_names: Optional[dict[str, str]] = None


class CapsuleSearchResults(SearchMeta):
    """Compact results: {items: [{id, n, s, d, t}], has_more, next_token, item_count}.

    Item fields: id=id, n=name, s=slug, d=description (truncated), t=tags (limited).
    Pagination: item_count returns the number of items in the current page.
      Use next_token for additional pages when has_more=true.
    Set include_field_names=true to add field_names with full labels.
    Use get_capsule(id) if full details needed.
    """

    items: list[CompactCapsuleItem]
    FIELD_NAMES: ClassVar[dict[str, str]] = {"id": "id", "n": "name", "s": "slug", "d": "description", "t": "tags"}

    @classmethod
    def from_sdk_results(cls, sdk_results: Any, include_field_names: bool = False) -> "CapsuleSearchResults":
        """Convert SDK search results to compact format."""
        items = [
            CompactCapsuleItem(
                id=c.id,
                n=c.name,
                s=c.slug,
                d=truncate_description(c.description),
                t=limit_tags(c.tags),
            )
            for c in sdk_results.results
        ]
        return cls(
            items=items,
            has_more=sdk_results.has_more,
            next_token=getattr(sdk_results, "next_token", None),
            item_count=len(items),
            field_names=cls.FIELD_NAMES if include_field_names else None,
        )


class DataAssetSearchResults(SearchMeta):
    """Compact results: {items: [{id, n, d, t}], has_more, next_token, item_count}.

    Item fields: id=id, n=name, d=description (truncated), t=tags (limited).
    Pagination: item_count returns the number of items in the current page.
      Use next_token for additional pages when has_more=true.
    Set include_field_names=true to add field_names with full labels.
    Use get_data_asset(id) if full details needed.
    """

    items: list[CompactDataAssetItem]
    FIELD_NAMES: ClassVar[dict[str, str]] = {"id": "id", "n": "name", "d": "description", "t": "tags"}

    @classmethod
    def from_sdk_results(cls, sdk_results: Any, include_field_names: bool = False) -> "DataAssetSearchResults":
        """Convert SDK search results to compact format."""
        items = [
            CompactDataAssetItem(
                id=d.id,
                n=d.name,
                d=truncate_description(d.description),
                t=limit_tags(d.tags),
            )
            for d in sdk_results.results
        ]
        return cls(
            items=items,
            has_more=sdk_results.has_more,
            next_token=getattr(sdk_results, "next_token", None),
            item_count=len(items),
            field_names=cls.FIELD_NAMES if include_field_names else None,
        )
