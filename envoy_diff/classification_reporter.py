"""Format ClassifiedResult into text, JSON, and Markdown outputs."""
from __future__ import annotations

import json
from typing import List

from envoy_diff.classifier import ClassifiedResult, KeyCategory


def _text_lines(cr: ClassifiedResult) -> List[str]:
    lines: List[str] = [
        f"Classification Report",
        f"  Source : {cr.source_path}",
        f"  Target : {cr.target_path}",
        "",
    ]
    active = cr.all_categories()
    if not active:
        lines.append("  No keys found.")
        return lines
    for cat in KeyCategory:
        keys = cr.keys_in(cat)
        if not keys:
            continue
        lines.append(f"  [{cat.value.upper()}]  ({len(keys)} key(s))")
        for k in keys:
            lines.append(f"    - {k}")
    return lines


def format_classification_text(cr: ClassifiedResult) -> str:
    return "\n".join(_text_lines(cr))


def format_classification_json(cr: ClassifiedResult) -> str:
    payload = {
        "source_path": cr.source_path,
        "target_path": cr.target_path,
        "categories": {
            cat.value: cr.keys_in(cat)
            for cat in KeyCategory
            if cr.keys_in(cat)
        },
    }
    return json.dumps(payload, indent=2)


def format_classification_markdown(cr: ClassifiedResult) -> str:
    lines: List[str] = [
        "## Classification Report",
        f"- **Source**: `{cr.source_path}`",
        f"- **Target**: `{cr.target_path}`",
        "",
    ]
    for cat in KeyCategory:
        keys = cr.keys_in(cat)
        if not keys:
            continue
        lines.append(f"### {cat.value.replace('_', ' ').title()} ({len(keys)})")        
        for k in keys:
            lines.append(f"- `{k}`")
        lines.append("")
    return "\n".join(lines)


def render_classification(cr: ClassifiedResult, fmt: str = "text") -> str:
    fmt = fmt.lower()
    if fmt == "json":
        return format_classification_json(cr)
    if fmt in ("md", "markdown"):
        return format_classification_markdown(cr)
    return format_classification_text(cr)
