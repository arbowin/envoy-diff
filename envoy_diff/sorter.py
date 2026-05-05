"""Sorting utilities for DiffResult entries."""

from enum import Enum
from typing import List

from envoy_diff.comparator import DiffResult


class SortKey(str, Enum):
    KEY = "key"
    STATUS = "status"


_STATUS_ORDER = {
    "missing_in_target": 0,
    "missing_in_source": 1,
    "mismatch": 2,
}


def _status_of(entry: dict) -> str:
    """Derive a status label from a diff entry dict."""
    if entry.get("source_value") is None and entry.get("target_value") is not None:
        return "missing_in_source"
    if entry.get("target_value") is None and entry.get("source_value") is not None:
        return "missing_in_target"
    return "mismatch"


def sort_result(result: DiffResult, sort_by: SortKey = SortKey.KEY, reverse: bool = False) -> DiffResult:
    """Return a new DiffResult with difference entries sorted.

    Args:
        result: The DiffResult to sort.
        sort_by: Sort criterion — either 'key' (alphabetical) or 'status' (by severity).
        reverse: If True, reverse the sort order.

    Returns:
        A new DiffResult instance with sorted differences.
    """
    differences: List[dict] = list(result.differences)

    if sort_by == SortKey.KEY:
        differences.sort(key=lambda e: e["key"].lower(), reverse=reverse)
    elif sort_by == SortKey.STATUS:
        differences.sort(
            key=lambda e: _STATUS_ORDER.get(_status_of(e), 99),
            reverse=reverse,
        )

    return DiffResult(
        differences=differences,
        source_only=result.source_only,
        target_only=result.target_only,
    )
