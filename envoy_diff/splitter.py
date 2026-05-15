"""Split a DiffResult into per-environment slices based on key prefixes or patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_diff.comparator import DiffResult


@dataclass
class SplitSlice:
    """A named subset of a DiffResult."""

    name: str
    result: DiffResult

    @property
    def key_count(self) -> int:
        return len(self.result.keys())


@dataclass
class SplitResult:
    """Collection of named slices produced by splitting a DiffResult."""

    slices: List[SplitSlice] = field(default_factory=list)
    unmatched: DiffResult = field(default_factory=dict)

    def get(self, name: str) -> Optional[SplitSlice]:
        for s in self.slices:
            if s.name == name:
                return s
        return None

    @property
    def slice_names(self) -> List[str]:
        return [s.name for s in self.slices]


class SplitterError(Exception):
    """Raised when split configuration is invalid."""


def split_result(
    result: DiffResult,
    rules: Dict[str, str],
    *,
    use_regex: bool = False,
) -> SplitResult:
    """Split *result* into named slices according to *rules*.

    Args:
        result: The DiffResult mapping to split.
        rules: Mapping of slice name -> prefix (or regex pattern when
               *use_regex* is True).
        use_regex: When True, treat rule values as full regex patterns.

    Returns:
        A SplitResult containing one SplitSlice per rule plus an
        ``unmatched`` dict for keys that matched no rule.
    """
    if not rules:
        raise SplitterError("rules mapping must not be empty")

    compiled: Dict[str, re.Pattern] = {}
    for name, pattern in rules.items():
        try:
            compiled[name] = re.compile(pattern if use_regex else re.escape(pattern))
        except re.error as exc:
            raise SplitterError(f"Invalid pattern for rule '{name}': {exc}") from exc

    buckets: Dict[str, DiffResult] = {name: {} for name in rules}
    unmatched: DiffResult = {}

    for key, entry in result.items():
        matched = False
        for name, rx in compiled.items():
            if rx.match(key):
                buckets[name][key] = entry
                matched = True
                break
        if not matched:
            unmatched[key] = entry

    slices = [SplitSlice(name=name, result=buckets[name]) for name in rules]
    return SplitResult(slices=slices, unmatched=unmatched)
