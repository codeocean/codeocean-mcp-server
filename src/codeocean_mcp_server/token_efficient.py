import re
from typing import Any, Optional

from pydantic import BaseModel

# Constants
MAX_DESCRIPTION_LENGTH = 200
MAX_TAGS_COUNT = 10
TRUNCATION_SUFFIX = "...(more)"
TAGS_TRUNCATION_MARKER = "..more.."


class CompactSearchMeta(BaseModel):
    """Metadata for compact search results."""

    has_more: bool
    next_token: Optional[str] = None
    total_returned: int
    result_type: str  # "capsule", "pipeline", or "data_asset"
    field_names: Optional[dict[str, str]] = None


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


class CompactCapsuleResult(BaseModel):
    """Compact search result for capsules/pipelines."""

    items: list[CompactCapsuleItem]
    meta: CompactSearchMeta


class CompactDataAssetResult(BaseModel):
    """Compact search result for data assets."""

    items: list[CompactDataAssetItem]
    meta: CompactSearchMeta


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


def get_field(item: Any, name: str, default: Any = "") -> Any:
    """Get field from item, supporting both dicts and objects."""
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def extract_compact_item(item: Any, include_slug: bool = False) -> dict[str, Any]:
    """Extract compact item data from a search result item."""
    item_id = get_field(item, "id", "")
    name = get_field(item, "name", "")
    description = truncate_description(get_field(item, "description", None))
    tags = limit_tags(get_field(item, "tags", None))

    if include_slug:
        slug = get_field(item, "slug", "")
        return {"id": item_id, "n": name, "s": slug, "d": description, "t": tags}
    return {"id": item_id, "n": name, "d": description, "t": tags}


def to_compact_result(
    results: list[Any],
    has_more: bool,
    next_token: Optional[str],
    result_type: str,
    include_field_names: bool = False,
) -> CompactCapsuleResult | CompactDataAssetResult:
    """Convert search results to compact object format."""
    include_slug = result_type in ("capsule", "pipeline")
    items = [extract_compact_item(item, include_slug=include_slug) for item in results]
    meta = CompactSearchMeta(
        has_more=has_more,
        next_token=next_token,
        total_returned=len(items),
        result_type=result_type,
    )
    if include_field_names:
        # Optional mapping keeps a single schema while allowing dynamic labeling.
        meta.field_names = (
            {"id": "id", "n": "name", "s": "slug", "d": "description", "t": "tags"}
            if include_slug
            else {"id": "id", "n": "name", "d": "description", "t": "tags"}
        )

    if include_slug:
        return CompactCapsuleResult(items=items, meta=meta)
    return CompactDataAssetResult(items=items, meta=meta)
