"""Validation helpers for parsed .env key/value pairs."""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_VALID_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
_SHELL_SPECIAL_RE = re.compile(r'[\$`!;&|<>]')


class ValidationError(ValueError):
    """Raised for hard validation failures."""


@dataclass
class ValidationWarning:
    """A non-fatal issue found during validation."""
    key: str
    message: str


@dataclass
class ValidationResult:
    """Aggregated result of validating an env mapping."""
    warnings: List[ValidationWarning] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.warnings) == 0

    def add(self, key: str, message: str) -> None:
        self.warnings.append(ValidationWarning(key=key, message=message))


def is_valid(key: str) -> bool:
    """Return True if *key* is a well-formed environment variable name."""
    return bool(_VALID_KEY_RE.match(key))


def add(result: ValidationResult, key: str, message: str) -> None:
    """Convenience wrapper to add a warning to *result*."""
    result.add(key, message)


def validate_env(env: Dict[str, Optional[str]]) -> ValidationResult:
    """Validate all keys and values in *env*, returning a ValidationResult.

    Checks performed:
    - Key contains a hyphen (not POSIX-portable).
    - Key contains whitespace.
    - Key starts with a digit.
    - Key is otherwise non-standard (fails _VALID_KEY_RE).
    - Value contains unquoted shell-special characters.
    """
    result = ValidationResult()

    for key, value in env.items():
        if re.search(r'-', key):
            result.add(key, "Key contains a hyphen; not portable across all shells.")
        elif re.search(r'\s', key):
            result.add(key, "Key contains whitespace; this is invalid.")
        elif re.match(r'^\d', key):
            result.add(key, "Key starts with a digit; this is invalid.")
        elif not is_valid(key):
            result.add(key, "Key contains non-standard characters.")

        if value is not None and _SHELL_SPECIAL_RE.search(value):
            result.add(key, "Value contains shell-special characters that may need quoting.")

    return result
