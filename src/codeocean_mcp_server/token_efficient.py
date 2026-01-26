import re
from typing import Any, Optional

from pydantic import BaseModel

# Constants
MAX_DESCRIPTION_LENGTH = 200
MAX_TAGS_COUNT = 10
TRUNCATION_SUFFIX = "...(more)"
TAGS_TRUNCATION_MARKER = "..more.."
CAPSULE_COLUMNS = ["id", "name", "slug", "description", "tags"]
DATA_ASSET_COLUMNS = ["id", "name", "description", "tags"]


class CompactSearchMeta(BaseModel):
    """Metadata for compact search results."""

    has_more: bool
    next_token: Optional[str] = None
    total_returned: int
    result_type: str  # "capsule", "pipeline", or "data_asset"


class CompactTableResult(BaseModel):
    """Token-efficient table format for search results."""

    cols: list[str]
    rows: list[list[Any]]
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


def extract_compact_row(item: Any, include_slug: bool = False) -> list[Any]:
    """Extract compact row data from a search result item."""
    item_id = get_field(item, "id", "")
    name = get_field(item, "name", "")
    description = truncate_description(get_field(item, "description", None))
    tags = limit_tags(get_field(item, "tags", None))

    if include_slug:
        slug = get_field(item, "slug", "")
        return [item_id, name, slug, description, tags]
    return [item_id, name, description, tags]


def to_compact_table(
    results: list[Any],
    has_more: bool,
    next_token: Optional[str],
    result_type: str,
) -> CompactTableResult:
    """Convert search results to compact table format."""
    include_slug = result_type in ("capsule", "pipeline")
    cols = CAPSULE_COLUMNS if include_slug else DATA_ASSET_COLUMNS

    rows = [extract_compact_row(item, include_slug=include_slug) for item in results]

    return CompactTableResult(
        cols=cols,
        rows=rows,
        meta=CompactSearchMeta(
            has_more=has_more,
            next_token=next_token,
            total_returned=len(rows),
            result_type=result_type,
        ),
    )
