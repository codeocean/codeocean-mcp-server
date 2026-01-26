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

    # Light whitespace normalization: collapse 3+ consecutive whitespace to single space
    normalized = re.sub(r"\s{3,}", " ", description).strip()

    # After normalization, check if empty
    if not normalized:
        return None

    if len(normalized) <= max_length:
        return normalized

    # Reserve space for suffix
    truncate_at = max_length - len(TRUNCATION_SUFFIX)

    # Try word boundary truncation
    last_space = normalized.rfind(" ", 0, truncate_at)

    if last_space > max_length // 2:  # Found reasonable break point
        return normalized[:last_space].rstrip() + TRUNCATION_SUFFIX
    else:  # No good break point, hard cut
        return normalized[:truncate_at].rstrip() + TRUNCATION_SUFFIX


def limit_tags(tags: Optional[list[str]], max_count: int = MAX_TAGS_COUNT) -> list[str]:
    """Limit tags to maximum count with truncation marker."""
    if not tags:
        return []

    if len(tags) <= max_count:
        return list(tags)  # Return a copy

    # Take first (max_count - 1) + marker to indicate more exist
    return list(tags[: max_count - 1]) + [TAGS_TRUNCATION_MARKER]


def extract_compact_row(item: Any, include_slug: bool = False) -> list[Any]:
    """Extract compact row data from a search result item."""

    def get_field(name: str, default: Any = "") -> Any:
        if isinstance(item, dict):
            return item.get(name, default)
        return getattr(item, name, default)

    item_id = get_field("id", "")
    name = get_field("name", "")
    description = truncate_description(get_field("description", None))
    tags = limit_tags(get_field("tags", None))

    if include_slug:
        slug = get_field("slug", "")
        return [item_id, name, slug, description, tags]
    else:
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
