"""Format a :class:`TaggedResult` as text, JSON, or Markdown."""

from __future__ import annotations

import json
from typing import List

from envoy_diff.tagger import TaggedResult


def _text_lines(tagged: TaggedResult) -> List[str]:
    lines: List[str] = []
    if not tagged.entries:
        lines.append("No tagged entries.")
        return lines

    all_tags = tagged.all_tags()
    lines.append(f"Tags present: {', '.join(all_tags) if all_tags else 'none'}")
    lines.append("")
    for entry in tagged.entries:
        tag_str = ", ".join(entry.tags) if entry.tags else "(untagged)"
        lines.append(f"  {entry.key}  [{tag_str}]")
    return lines


def format_tag_text(tagged: TaggedResult) -> str:
    return "\n".join(_text_lines(tagged))


def format_tag_json(tagged: TaggedResult) -> str:
    payload = {
        "tags": tagged.all_tags(),
        "entries": [
            {
                "key": e.key,
                "source_value": e.source_value,
                "target_value": e.target_value,
                "tags": e.tags,
            }
            for e in tagged.entries
        ],
    }
    return json.dumps(payload, indent=2)


def format_tag_markdown(tagged: TaggedResult) -> str:
    lines: List[str] = ["## Tagged Diff Entries", ""]
    if not tagged.entries:
        lines.append("_No tagged entries._")
        return "\n".join(lines)

    lines.append("| Key | Tags |")
    lines.append("|-----|------|")
    for entry in tagged.entries:
        tag_str = ", ".join(entry.tags) if entry.tags else "_(untagged)_"
        lines.append(f"| `{entry.key}` | {tag_str} |")
    return "\n".join(lines)


def render_tag(tagged: TaggedResult, fmt: str = "text") -> str:
    """Render *tagged* in the requested *fmt* (``text``, ``json``, ``markdown``)."""
    fmt = fmt.lower()
    if fmt == "json":
        return format_tag_json(tagged)
    if fmt in {"md", "markdown"}:
        return format_tag_markdown(tagged)
    return format_tag_text(tagged)
