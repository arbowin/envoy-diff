"""Comparator module for diffing two parsed .env file dictionaries."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class DiffResult:
    """Holds the result of comparing two .env file dictionaries."""

    missing_in_target: Dict[str, Optional[str]] = field(default_factory=dict)
    missing_in_source: Dict[str, Optional[str]] = field(default_factory=dict)
    mismatched: Dict[str, tuple] = field(default_factory=dict)
    matching: Dict[str, Optional[str]] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        """Return True if any differences were found."""
        return bool(
            self.missing_in_target or self.missing_in_source or self.mismatched
        )

    def summary(self) -> str:
        """Return a human-readable summary of the diff."""
        lines = []
        if self.missing_in_target:
            lines.append(f"Missing in target ({len(self.missing_in_target)}):")
            for key in sorted(self.missing_in_target):
                lines.append(f"  - {key}")
        if self.missing_in_source:
            lines.append(f"Missing in source ({len(self.missing_in_source)}):")
            for key in sorted(self.missing_in_source):
                lines.append(f"  + {key}")
        if self.mismatched:
            lines.append(f"Mismatched values ({len(self.mismatched)}):")
            for key in sorted(self.mismatched):
                src_val, tgt_val = self.mismatched[key]
                lines.append(f"  ~ {key}: {src_val!r} -> {tgt_val!r}")
        if not lines:
            lines.append("No differences found.")
        return "\n".join(lines)


def compare_envs(
    source: Dict[str, Optional[str]],
    target: Dict[str, Optional[str]],
) -> DiffResult:
    """Compare two env dictionaries and return a DiffResult.

    Args:
        source: The reference environment (e.g. .env.example).
        target: The environment being checked (e.g. .env.production).

    Returns:
        A DiffResult describing all differences.
    """
    result = DiffResult()
    all_keys = set(source) | set(target)

    for key in all_keys:
        in_source = key in source
        in_target = key in target

        if in_source and not in_target:
            result.missing_in_target[key] = source[key]
        elif in_target and not in_source:
            result.missing_in_source[key] = target[key]
        elif source[key] != target[key]:
            result.mismatched[key] = (source[key], target[key])
        else:
            result.matching[key] = source[key]

    return result
