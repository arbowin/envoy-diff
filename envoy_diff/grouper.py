"""Group diff results by key prefix (e.g. DB_, AWS_, APP_)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_diff.comparator import DiffResult


@dataclass
class GroupedResult:
    """DiffResult entries partitioned by key prefix."""

    groups: Dict[str, DiffResult] = field(default_factory=dict)
    separator: str = "_"

    def prefix_of(self, key: str) -> str:
        """Return the first segment of *key* before the separator, uppercased."""
        idx = key.find(self.separator)
        return key[:idx].upper() if idx > 0 else key.upper()

    @property
    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def get(self, name: str) -> Optional[DiffResult]:
        return self.groups.get(name)


def group_result(
    result: DiffResult,
    separator: str = "_",
) -> GroupedResult:
    """Partition *result* entries into sub-DiffResults keyed by prefix.

    Keys without a separator are placed under their full uppercased name.
    """
    grouped = GroupedResult(separator=separator)

    all_keys: List[tuple] = (
        [(k, v, None) for k, v in (result.missing_in_target or {}).items()]
        + [(k, None, v) for k, v in (result.missing_in_source or {}).items()]
        + [
            (k, sv, tv)
            for k, (sv, tv) in (result.mismatched or {}).items()
        ]
        + [(k, v, v) for k, v in (result.matching or {}).items()]
    )

    buckets: Dict[str, dict] = {}
    for key, src_val, tgt_val in all_keys:
        idx = key.find(separator)
        prefix = key[:idx].upper() if idx > 0 else key.upper()
        buckets.setdefault(prefix, {"missing_in_target": {}, "missing_in_source": {}, "mismatched": {}, "matching": {}})
        b = buckets[prefix]
        if src_val is not None and tgt_val is None and key in (result.missing_in_target or {}):
            b["missing_in_target"][key] = src_val
        elif tgt_val is not None and src_val is None and key in (result.missing_in_source or {}):
            b["missing_in_source"][key] = tgt_val
        elif key in (result.mismatched or {}):
            b["mismatched"][key] = (src_val, tgt_val)
        else:
            b["matching"][key] = src_val

    for prefix, parts in buckets.items():
        grouped.groups[prefix] = DiffResult(
            missing_in_target=parts["missing_in_target"],
            missing_in_source=parts["missing_in_source"],
            mismatched=parts["mismatched"],
            matching=parts["matching"],
        )

    return grouped
