"""Redact sensitive values in diff results before display or export."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from envoy_diff.comparator import DiffResult

_DEFAULT_PATTERNS: List[str] = [
    r"(?i)(password|passwd|secret|token|api_key|apikey|private_key|auth)",
]

REDACTED_PLACEHOLDER = "***REDACTED***"


@dataclass
class RedactOptions:
    """Options controlling which keys are redacted."""

    patterns: List[str] = field(default_factory=lambda: list(_DEFAULT_PATTERNS))
    placeholder: str = REDACTED_PLACEHOLDER
    case_sensitive: bool = False


class RedactError(Exception):
    """Raised when redaction configuration is invalid."""


def _compile_patterns(options: RedactOptions) -> List[re.Pattern]:
    flags = 0 if options.case_sensitive else re.IGNORECASE
    compiled = []
    for raw in options.patterns:
        try:
            compiled.append(re.compile(raw, flags))
        except re.error as exc:
            raise RedactError(f"Invalid redact pattern {raw!r}: {exc}") from exc
    return compiled


def _should_redact(key: str, patterns: List[re.Pattern]) -> bool:
    return any(p.search(key) for p in patterns)


def _redact_value(value: Optional[str], placeholder: str) -> Optional[str]:
    return placeholder if value is not None else None


def redact_result(result: DiffResult, options: Optional[RedactOptions] = None) -> DiffResult:
    """Return a new DiffResult with sensitive values replaced by the placeholder.

    Keys whose names match any of the configured patterns have both their
    source and target values replaced.  Keys that are missing entirely
    (value is ``None``) remain ``None`` so that presence/absence information
    is preserved.
    """
    if options is None:
        options = RedactOptions()

    patterns = _compile_patterns(options)
    ph = options.placeholder

    redacted_diffs: dict = {}
    for key, (src, tgt) in result.diffs.items():
        if _should_redact(key, patterns):
            redacted_diffs[key] = (_redact_value(src, ph), _redact_value(tgt, ph))
        else:
            redacted_diffs[key] = (src, tgt)

    return DiffResult(diffs=redacted_diffs)
