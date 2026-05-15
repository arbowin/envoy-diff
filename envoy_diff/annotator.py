"""Annotate diff results with human-readable descriptions and hints."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envoy_diff.comparator import DiffResult


@dataclass
class Annotation:
    """A single annotation attached to a diff key."""

    key: str
    status: str  # 'missing_in_target', 'missing_in_source', 'mismatch', 'ok'
    hint: str

    def __str__(self) -> str:
        return f"[{self.status}] {self.key}: {self.hint}"


@dataclass
class AnnotatedResult:
    """DiffResult enriched with per-key annotations."""

    diff: DiffResult
    annotations: List[Annotation] = field(default_factory=list)

    @property
    def has_annotations(self) -> bool:
        return len(self.annotations) > 0

    def by_status(self, status: str) -> List[Annotation]:
        return [a for a in self.annotations if a.status == status]

    def summary(self) -> str:
        """Return a short human-readable summary of the annotation counts."""
        missing_target = len(self.by_status("missing_in_target"))
        missing_source = len(self.by_status("missing_in_source"))
        mismatched = len(self.by_status("mismatch"))
        parts = []
        if missing_target:
            parts.append(f"{missing_target} missing in target")
        if missing_source:
            parts.append(f"{missing_source} missing in source")
        if mismatched:
            parts.append(f"{mismatched} mismatched")
        return ", ".join(parts) if parts else "no differences found"


_HINTS = {
    "missing_in_target": "Key exists in source but is absent from target — add it to keep environments in sync.",
    "missing_in_source": "Key exists in target but is absent from source — verify whether it should be back-ported.",
    "mismatch": "Key is present in both environments but values differ — confirm the divergence is intentional.",
}


def annotate_result(diff: DiffResult) -> AnnotatedResult:
    """Produce an AnnotatedResult from a DiffResult."""
    annotations: List[Annotation] = []

    for key in sorted(diff.missing_in_target):
        annotations.append(Annotation(key=key, status="missing_in_target", hint=_HINTS["missing_in_target"]))

    for key in sorted(diff.missing_in_source):
        annotations.append(Annotation(key=key, status="missing_in_source", hint=_HINTS["missing_in_source"]))

    for key in sorted(diff.mismatched):
        annotations.append(Annotation(key=key, status="mismatch", hint=_HINTS["mismatch"]))

    return AnnotatedResult(diff=diff, annotations=annotations)
