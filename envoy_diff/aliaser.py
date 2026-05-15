"""Key alias resolution: map legacy/alternate key names to canonical keys before diffing."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class AliasRule:
    """Maps one or more alias keys to a single canonical key."""
    canonical: str
    aliases: List[str]

    def matches(self, key: str) -> bool:
        return key in self.aliases


@dataclass
class AliasMatch:
    """Records a resolved alias substitution."""
    original_key: str
    canonical_key: str
    rule: AliasRule


@dataclass
class AliasResult:
    """Outcome of applying alias rules to an env mapping."""
    resolved: Dict[str, Optional[str]]
    matches: List[AliasMatch] = field(default_factory=list)
    unresolved_keys: List[str] = field(default_factory=list)

    @property
    def has_matches(self) -> bool:
        return bool(self.matches)


class AliasError(Exception):
    """Raised when alias configuration is invalid."""


def _validate_rules(rules: List[AliasRule]) -> None:
    canonical_names = [r.canonical for r in rules]
    if len(canonical_names) != len(set(canonical_names)):
        raise AliasError("Duplicate canonical key names in alias rules.")


def apply_aliases(
    env: Dict[str, Optional[str]],
    rules: List[AliasRule],
) -> AliasResult:
    """Return a new env mapping with alias keys replaced by their canonical names.

    If both an alias key and its canonical key exist in *env*, the canonical
    key takes precedence and the alias entry is dropped.
    """
    _validate_rules(rules)

    alias_map: Dict[str, AliasRule] = {}
    for rule in rules:
        for alias in rule.aliases:
            alias_map[alias] = rule

    resolved: Dict[str, Optional[str]] = {}
    matches: List[AliasMatch] = []
    unresolved: List[str] = []

    for key, value in env.items():
        if key in alias_map:
            rule = alias_map[key]
            canonical = rule.canonical
            if canonical not in env:
                resolved[canonical] = value
                matches.append(AliasMatch(original_key=key, canonical_key=canonical, rule=rule))
            # else: canonical already present — skip alias silently
        else:
            resolved[key] = value
            if key not in {r.canonical for r in rules}:
                unresolved.append(key)

    return AliasResult(resolved=resolved, matches=matches, unresolved_keys=unresolved)
