"""Render AnnotatedResult to text, JSON, and Markdown."""

from __future__ import annotations

import json
from typing import List

from envoy_diff.annotator import AnnotatedResult


def _text_lines(ar: AnnotatedResult) -> List[str]:
    lines: List[str] = []
    if not ar.has_annotations:
        lines.append("No annotations — environments are in sync.")
        return lines
    for ann in ar.annotations:
        lines.append(str(ann))
    return lines


def format_annotation_text(ar: AnnotatedResult) -> str:
    """Plain-text rendering of annotations."""
    return "\n".join(_text_lines(ar))


def format_annotation_json(ar: AnnotatedResult) -> str:
    """JSON rendering of annotations."""
    payload = [
        {"key": a.key, "status": a.status, "hint": a.hint}
        for a in ar.annotations
    ]
    return json.dumps(payload, indent=2)


def format_annotation_markdown(ar: AnnotatedResult) -> str:
    """Markdown rendering of annotations."""
    if not ar.has_annotations:
        return "_No annotations — environments are in sync._"
    lines = ["| Key | Status | Hint |", "|-----|--------|------|"]
    for ann in ar.annotations:
        lines.append(f"| `{ann.key}` | {ann.status} | {ann.hint} |")
    return "\n".join(lines)


def render_annotation(ar: AnnotatedResult, fmt: str = "text") -> str:
    """Dispatch to the appropriate formatter.

    Args:
        ar: The annotated diff result.
        fmt: One of 'text', 'json', 'markdown'.

    Returns:
        Formatted string.

    Raises:
        ValueError: If *fmt* is not recognised.
    """
    fmt = fmt.lower()
    if fmt == "text":
        return format_annotation_text(ar)
    if fmt == "json":
        return format_annotation_json(ar)
    if fmt in ("markdown", "md"):
        return format_annotation_markdown(ar)
    raise ValueError(f"Unknown annotation format: {fmt!r}")
