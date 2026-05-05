"""Filtering utilities for DiffResult — allow users to narrow results by key pattern or diff type."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import Optional

from envoy_diff.comparator import DiffResult


@dataclass
class FilterOptions:
    """Options controlling which diff entries are included in output."""

    pattern: Optional[str] = None  # glob or regex pattern to match keys
    use_regex: bool = False
    include_missing_in_target: bool = True
    include_missing_in_source: bool = True
    include_mismatched: bool = True


def _key_matches(key: str, options: FilterOptions) -> bool:
    """Return True if *key* matches the pattern in *options* (or no pattern set)."""
    if options.pattern is None:
        return True
    if options.use_regex:
        return bool(re.search(options.pattern, key))
    return fnmatch.fnmatch(key, options.pattern)


def filter_result(result: DiffResult, options: FilterOptions) -> DiffResult:
    """Return a new :class:`DiffResult` containing only entries that satisfy *options*."""
    missing_in_target = (
        {k: v for k, v in result.missing_in_target.items() if _key_matches(k, options)}
        if options.include_missing_in_target
        else {}
    )
    missing_in_source = (
        {k: v for k, v in result.missing_in_source.items() if _key_matches(k, options)}
        if options.include_missing_in_source
        else {}
    )
    mismatched = (
        {
            k: v
            for k, v in result.mismatched.items()
            if _key_matches(k, options)
        }
        if options.include_mismatched
        else {}
    )

    return DiffResult(
        missing_in_target=missing_in_target,
        missing_in_source=missing_in_source,
        mismatched=mismatched,
    )
