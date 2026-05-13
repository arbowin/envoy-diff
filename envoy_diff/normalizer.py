"""Normalize DiffResult entries for consistent comparison.

Provides options to strip whitespace, normalize case, and expand
common value aliases (e.g. 'true'/'True'/'TRUE' -> 'true') before
diffing so that cosmetic differences are not flagged as mismatches.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envoy_diff.comparator import DiffResult


_BOOL_TRUE = frozenset({"true", "1", "yes", "on"})
_BOOL_FALSE = frozenset({"false", "0", "no", "off"})


@dataclass
class NormalizeOptions:
    """Controls which normalizations are applied."""

    strip_whitespace: bool = True
    lowercase_values: bool = False
    normalize_booleans: bool = False
    normalize_empty_to_none: bool = False


def _normalize_value(
    value: Optional[str], opts: NormalizeOptions
) -> Optional[str]:
    """Apply all enabled normalizations to a single value."""
    if value is None:
        return None

    if opts.strip_whitespace:
        value = value.strip()

    if opts.normalize_empty_to_none and value == "":
        return None

    if opts.lowercase_values:
        value = value.lower()

    if opts.normalize_booleans:
        lower = value.lower()
        if lower in _BOOL_TRUE:
            return "true"
        if lower in _BOOL_FALSE:
            return "false"

    return value


def normalize_result(
    result: DiffResult, opts: Optional[NormalizeOptions] = None
) -> DiffResult:
    """Return a new DiffResult with normalized source/target values.

    Entries whose source and target values become equal after
    normalization are removed from the result (no longer mismatches).
    Entries that are missing in source or target are kept unchanged.
    """
    if opts is None:
        opts = NormalizeOptions()

    normalized_diffs: dict[str, tuple[Optional[str], Optional[str]]] = {}

    for key, (src, tgt) in result.differences.items():
        norm_src = _normalize_value(src, opts)
        norm_tgt = _normalize_value(tgt, opts)
        # Only keep the entry if it still represents a real difference
        if norm_src != norm_tgt:
            normalized_diffs[key] = (norm_src, norm_tgt)

    return DiffResult(differences=normalized_diffs)
