"""Generate patch suggestions to reconcile differences between .env files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_diff.comparator import DiffResult


class PatchError(Exception):
    """Raised when patch generation fails."""


@dataclass
class PatchEntry:
    """A single suggested change to apply to the target env."""

    key: str
    action: str  # 'add', 'remove', 'update'
    source_value: Optional[str]
    target_value: Optional[str]

    def as_line(self) -> str:
        """Return the env line that should be written for 'add' or 'update'."""
        if self.action == "remove":
            return f"# REMOVE: {self.key}"
        value = self.source_value if self.source_value is not None else ""
        return f"{self.key}={value}"


@dataclass
class PatchResult:
    """Collection of patch entries derived from a DiffResult."""

    entries: List[PatchEntry] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def by_action(self, action: str) -> List[PatchEntry]:
        return [e for e in self.entries if e.action == action]


def generate_patch(
    result: DiffResult,
    *,
    include_removals: bool = False,
) -> PatchResult:
    """Build a PatchResult from a DiffResult.

    Args:
        result: The diff result to derive patches from.
        include_removals: When True, include entries for keys present in target
            but missing in source (suggesting removal from target).

    Returns:
        A PatchResult with one PatchEntry per actionable difference.
    """
    entries: List[PatchEntry] = []

    for key, src_val in result.missing_in_target.items():
        entries.append(
            PatchEntry(key=key, action="add", source_value=src_val, target_value=None)
        )

    if include_removals:
        for key, tgt_val in result.missing_in_source.items():
            entries.append(
                PatchEntry(
                    key=key, action="remove", source_value=None, target_value=tgt_val
                )
            )

    for key, (src_val, tgt_val) in result.mismatched.items():
        entries.append(
            PatchEntry(
                key=key, action="update", source_value=src_val, target_value=tgt_val
            )
        )

    entries.sort(key=lambda e: e.key)
    return PatchResult(entries=entries)


def patch_to_lines(patch: PatchResult) -> List[str]:
    """Render patch entries as env-file lines suitable for writing."""
    return [entry.as_line() for entry in patch.entries]
