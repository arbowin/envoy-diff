"""Render TemplateResult objects as text, JSON, or Markdown."""
from __future__ import annotations

import json
from typing import List

from envoy_diff.templater import TemplateResult


def _text_lines(result: TemplateResult) -> List[str]:
    lines = ["=== .env Template ==="]
    if result.key_count == 0:
        lines.append("(no keys to template)")
        return lines
    lines.append(f"Keys to fill in: {result.key_count}")
    lines.append("")
    for entry in result.entries:
        tag = f"[{entry.comment}]" if entry.comment else ""
        lines.append(f"  {entry.key}={entry.placeholder}  {tag}".rstrip())
    return lines


def format_template_text(result: TemplateResult) -> str:
    return "\n".join(_text_lines(result)) + "\n"


def format_template_json(result: TemplateResult) -> str:
    data = {
        "key_count": result.key_count,
        "entries": [
            {"key": e.key, "placeholder": e.placeholder, "comment": e.comment}
            for e in result.entries
        ],
    }
    return json.dumps(data, indent=2)


def format_template_markdown(result: TemplateResult) -> str:
    lines = ["## .env Template", ""]
    if result.key_count == 0:
        lines.append("_No keys to template._")
        return "\n".join(lines) + "\n"
    lines.append(f"**Keys to fill in:** {result.key_count}")
    lines.append("")
    lines.append("| Key | Placeholder | Note |")
    lines.append("|-----|-------------|------|")
    for entry in result.entries:
        note = entry.comment or ""
        lines.append(f"| `{entry.key}` | `{entry.placeholder}` | {note} |")
    return "\n".join(lines) + "\n"


def render_template(result: TemplateResult, fmt: str = "text") -> str:
    """Render *result* in the requested format (text/json/markdown)."""
    fmt = fmt.lower()
    if fmt == "json":
        return format_template_json(result)
    if fmt in ("md", "markdown"):
        return format_template_markdown(result)
    return format_template_text(result)
