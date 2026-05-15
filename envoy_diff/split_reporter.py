"""Render a SplitResult as text, JSON, or Markdown."""

from __future__ import annotations

import json
from typing import List

from envoy_diff.splitter import SplitResult
from envoy_diff.formatter import format_result, OutputFormat


def _text_lines(sr: SplitResult) -> List[str]:
    lines: List[str] = []
    for slc in sr.slices:
        lines.append(f"[{slc.name}] ({slc.key_count} keys)")
        if slc.key_count == 0:
            lines.append("  (no keys)")
        else:
            inner = format_result(slc.result, OutputFormat.TEXT)
            for ln in inner.splitlines():
                lines.append(f"  {ln}")
    if sr.unmatched:
        lines.append(f"[unmatched] ({len(sr.unmatched)} keys)")
        inner = format_result(sr.unmatched, OutputFormat.TEXT)
        for ln in inner.splitlines():
            lines.append(f"  {ln}")
    return lines


def format_split_text(sr: SplitResult) -> str:
    return "\n".join(_text_lines(sr))


def format_split_json(sr: SplitResult) -> str:
    payload = {
        "slices": [
            {
                "name": slc.name,
                "key_count": slc.key_count,
                "keys": list(slc.result.keys()),
            }
            for slc in sr.slices
        ],
        "unmatched": list(sr.unmatched.keys()),
    }
    return json.dumps(payload, indent=2)


def format_split_markdown(sr: SplitResult) -> str:
    lines: List[str] = []
    for slc in sr.slices:
        lines.append(f"### {slc.name} ({slc.key_count} keys)")
        if slc.key_count == 0:
            lines.append("_No keys._")
        else:
            inner = format_result(slc.result, OutputFormat.MARKDOWN)
            lines.append(inner)
    if sr.unmatched:
        lines.append(f"### unmatched ({len(sr.unmatched)} keys)")
        inner = format_result(sr.unmatched, OutputFormat.MARKDOWN)
        lines.append(inner)
    return "\n".join(lines)


def render_split(sr: SplitResult, fmt: str = "text") -> str:
    """Render *sr* in the requested format (text/json/markdown)."""
    fmt = fmt.lower()
    if fmt == "json":
        return format_split_json(sr)
    if fmt in ("md", "markdown"):
        return format_split_markdown(sr)
    return format_split_text(sr)
