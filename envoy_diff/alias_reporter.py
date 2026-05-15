"""Render AliasResult objects as text, JSON, or Markdown."""
from __future__ import annotations

import json
from typing import List

from envoy_diff.aliaser import AliasResult


def _text_lines(result: AliasResult) -> List[str]:
    lines: List[str] = []
    if not result.has_matches:
        lines.append("No alias substitutions applied.")
        return lines
    lines.append(f"Alias substitutions applied: {len(result.matches)}")
    for m in result.matches:
        lines.append(f"  {m.original_key!r} -> {m.canonical_key!r}")
    return lines


def format_alias_text(result: AliasResult) -> str:
    return "\n".join(_text_lines(result))


def format_alias_json(result: AliasResult) -> str:
    payload = {
        "substitutions": [
            {"original": m.original_key, "canonical": m.canonical_key}
            for m in result.matches
        ],
        "resolved_key_count": len(result.resolved),
    }
    return json.dumps(payload, indent=2)


def format_alias_markdown(result: AliasResult) -> str:
    lines: List[str] = ["## Alias Substitutions", ""]
    if not result.has_matches:
        lines.append("_No alias substitutions applied._")
        return "\n".join(lines)
    lines.append("| Original Key | Canonical Key |")
    lines.append("|---|---|")
    for m in result.matches:
        lines.append(f"| `{m.original_key}` | `{m.canonical_key}` |")
    return "\n".join(lines)


def render_alias(result: AliasResult, fmt: str = "text") -> str:
    """Render *result* in the requested format ('text', 'json', 'markdown')."""
    fmt = fmt.lower()
    if fmt == "json":
        return format_alias_json(result)
    if fmt in ("md", "markdown"):
        return format_alias_markdown(result)
    return format_alias_text(result)
