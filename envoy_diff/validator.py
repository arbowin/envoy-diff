"""Validator module for envoy-diff.

Provides utilities to validate parsed .env file contents,
checking for suspicious or malformed entries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class ValidationError(Exception):
    """Raised when a validation rule encounters a fatal issue."""


@dataclass
class ValidationWarning:
    key: str
    message: str


@dataclass
class ValidationResult:
    warnings: List[ValidationWarning] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.warnings) == 0

    def add(self, key: str, message: str) -> None:
        self.warnings.append(ValidationWarning(key=key, message=message))


_SUSPICIOUS_CHARS = set('<>|;&`$(){}[]')


def validate_env(env: Dict[str, Optional[str]]) -> ValidationResult:
    """Validate a parsed env dictionary and return a ValidationResult.

    Checks performed:
    - Keys must be non-empty and contain only alphanumeric characters or underscores.
    - Values containing shell-special characters are flagged.
    - Keys that start with a digit are flagged.
    """
    result = ValidationResult()

    for key, value in env.items():
        if not key:
            result.add(key, "Empty key detected.")
            continue

        if not all(c.isalnum() or c == '_' for c in key):
            result.add(key, f"Key '{key}' contains non-alphanumeric/underscore characters.")

        if key[0].isdigit():
            result.add(key, f"Key '{key}' starts with a digit.")

        if value is not None:
            found = [c for c in value if c in _SUSPICIOUS_CHARS]
            if found:
                chars = ', '.join(repr(c) for c in sorted(set(found)))
                result.add(key, f"Value for '{key}' contains suspicious characters: {chars}.")

    return result
