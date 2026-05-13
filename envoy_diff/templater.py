"""Generate .env template files from diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envoy_diff.comparator import DiffResult


class TemplateError(Exception):
    """Raised when template generation fails."""


@dataclass
class TemplateEntry:
    key: str
    placeholder: str
    comment: Optional[str] = None

    def as_line(self) -> str:
        parts = []
        if self.comment:
            parts.append(f"# {self.comment}")
        parts.append(f"{self.key}={self.placeholder}")
        return "\n".join(parts)


@dataclass
class TemplateResult:
    entries: List[TemplateEntry] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.entries)

    def as_text(self) -> str:
        if not self.entries:
            return ""
        return "\n".join(e.as_line() for e in self.entries) + "\n"


def _placeholder_for(key: str, value: Optional[str]) -> str:
    """Return a placeholder string for a template entry."""
    if value is not None and value != "":
        return value
    return f"<{key.lower()}>"


def generate_template(
    result: DiffResult,
    include_mismatched: bool = True,
    placeholder_override: Optional[str] = None,
) -> TemplateResult:
    """Build a TemplateResult from a DiffResult.

    Includes all keys that are missing in the target (i.e. need to be filled
    in) and optionally keys whose values differ between source and target.
    """
    entries: List[TemplateEntry] = []

    for key, value in sorted(result.missing_in_target.items()):
        placeholder = placeholder_override or _placeholder_for(key, value)
        entries.append(
            TemplateEntry(key=key, placeholder=placeholder, comment="missing")
        )

    if include_mismatched:
        for key, (src_val, _tgt_val) in sorted(result.mismatched.items()):
            placeholder = placeholder_override or _placeholder_for(key, src_val)
            entries.append(
                TemplateEntry(key=key, placeholder=placeholder, comment="mismatch")
            )

    return TemplateResult(entries=entries)


def write_template(result: DiffResult, path: str, **kwargs: object) -> None:
    """Write a template file to *path* derived from *result*."""
    template = generate_template(result, **kwargs)  # type: ignore[arg-type]
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(template.as_text())
    except OSError as exc:
        raise TemplateError(f"Cannot write template to {path!r}: {exc}") from exc
