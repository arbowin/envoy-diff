"""Key rename mapping: track old→new key aliases across environments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_diff.comparator import DiffResult


@dataclass
class RenameRule:
    """A single old-key → new-key mapping."""
    old_key: str
    new_key: str


@dataclass
class RenameMatch:
    """A key pair that satisfies a rename rule."""
    rule: RenameRule
    old_value: Optional[str]
    new_value: Optional[str]

    @property
    def values_match(self) -> bool:
        return self.old_value == self.new_value


@dataclass
class RenameResult:
    """Outcome of applying rename rules to a DiffResult."""
    source_path: str
    target_path: str
    matches: List[RenameMatch] = field(default_factory=list)
    unmatched_rules: List[RenameRule] = field(default_factory=list)

    @property
    def has_matches(self) -> bool:
        return bool(self.matches)

    @property
    def all_values_consistent(self) -> bool:
        """True when every matched rename pair carries the same value."""
        return all(m.values_match for m in self.matches)


class RenameError(Exception):
    """Raised when rename processing fails."""


def apply_renames(result: DiffResult, rules: List[RenameRule]) -> RenameResult:
    """Match rename rules against a DiffResult.

    For each rule, look for *old_key* in the source dict and *new_key* in the
    target dict (or vice-versa) and record whether their values agree.

    Args:
        result: Parsed diff between two .env files.
        rules:  List of RenameRule instances to evaluate.

    Returns:
        A RenameResult describing which rules matched and which did not.
    """
    if not isinstance(rules, list):
        raise RenameError("rules must be a list of RenameRule instances")

    source_map: Dict[str, Optional[str]] = {
        entry.key: entry.source_value for entry in result.entries
    }
    target_map: Dict[str, Optional[str]] = {
        entry.key: entry.target_value for entry in result.entries
    }

    rename_result = RenameResult(
        source_path=result.source_path,
        target_path=result.target_path,
    )

    for rule in rules:
        old_present = rule.old_key in source_map or rule.old_key in target_map
        new_present = rule.new_key in source_map or rule.new_key in target_map

        if old_present or new_present:
            old_val = source_map.get(rule.old_key) or target_map.get(rule.old_key)
            new_val = source_map.get(rule.new_key) or target_map.get(rule.new_key)
            rename_result.matches.append(
                RenameMatch(rule=rule, old_value=old_val, new_value=new_val)
            )
        else:
            rename_result.unmatched_rules.append(rule)

    return rename_result
