"""Tag diff entries with custom labels for categorisation and reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional

from envoy_diff.comparator import DiffResult


@dataclass
class TagRule:
    """A rule that maps a glob pattern to a tag label."""

    pattern: str
    tag: str


@dataclass
class TaggedEntry:
    """A single diff key decorated with zero or more tags."""

    key: str
    source_value: Optional[str]
    target_value: Optional[str]
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        tag_str = ", ".join(self.tags) if self.tags else "(untagged)"
        return f"{self.key} [{tag_str}]"


@dataclass
class TaggedResult:
    """Collection of tagged entries derived from a DiffResult."""

    entries: List[TaggedEntry] = field(default_factory=list)

    def by_tag(self, tag: str) -> List[TaggedEntry]:
        """Return all entries that carry *tag*."""
        return [e for e in self.entries if tag in e.tags]

    def all_tags(self) -> List[str]:
        """Sorted list of unique tags present in this result."""
        tags: set[str] = set()
        for entry in self.entries:
            tags.update(entry.tags)
        return sorted(tags)

    def __len__(self) -> int:
        return len(self.entries)


def _tags_for_key(key: str, rules: List[TagRule]) -> List[str]:
    """Return all tags whose pattern matches *key* (preserving rule order)."""
    seen: Dict[str, bool] = {}
    result: List[str] = []
    for rule in rules:
        if fnmatch(key, rule.pattern) and rule.tag not in seen:
            seen[rule.tag] = True
            result.append(rule.tag)
    return result


def tag_result(diff: DiffResult, rules: List[TagRule]) -> TaggedResult:
    """Apply *rules* to every key in *diff* and return a :class:`TaggedResult`."""
    all_keys = sorted(
        set(diff.missing_in_target)
        | set(diff.missing_in_source)
        | set(diff.mismatched)
    )
    entries: List[TaggedEntry] = []
    for key in all_keys:
        source_val = diff.mismatched.get(key, (None, None))[0] if key in diff.mismatched else None
        target_val = diff.mismatched.get(key, (None, None))[1] if key in diff.mismatched else None
        tags = _tags_for_key(key, rules)
        entries.append(TaggedEntry(key=key, source_value=source_val, target_value=target_val, tags=tags))
    return TaggedResult(entries=entries)
