"""Format a GroupedResult for text, JSON, and Markdown output."""

from __future__ import annotations

import json
from typing import List

from envoy_diff.comparator import has_differences
from envoy_diff.grouper import GroupedResult


def _text_lines(grouped: GroupedResult) -> List[str]:
    lines: List[str] = []
    for name in grouped.group_names:
        result = grouped.groups[name]
        diff_count = (
            len(result.missing_in_target or {})
            + len(result.missing_in_source or {})
            + len(result.mismatched or {})
        )
        status = f"{diff_count} issue(s)" if has_differences(result) else "OK"
        lines.append(f"[{name}] {status}")
        for k in sorted(result.missing_in_target or {}):
            lines.append(f"  - {k}: missing in target")
        for k in sorted(result.missing_in_source or {}):
            lines.append(f"  - {k}: missing in source")
        for k, (sv, tv) in sorted((result.mismatched or {}).items()):
            lines.append(f"  - {k}: '{sv}' != '{tv}'")
    return lines


def format_group_text(grouped: GroupedResult) -> str:
    lines = _text_lines(grouped)
    return "\n".join(lines) if lines else "No groups found."


def format_group_json(grouped: GroupedResult) -> str:
    payload = {}
    for name in grouped.group_names:
        r = grouped.groups[name]
        payload[name] = {
            "missing_in_target": list(sorted(r.missing_in_target or {})),
            "missing_in_source": list(sorted(r.missing_in_source or {})),
            "mismatched": {k: {"source": sv, "target": tv} for k, (sv, tv) in (r.mismatched or {}).items()},
            "matching_count": len(r.matching or {}),
        }
    return json.dumps(payload, indent=2)


def format_group_markdown(grouped: GroupedResult) -> str:
    lines: List[str] = ["## Grouped Diff Results", ""]
    for name in grouped.group_names:
        r = grouped.groups[name]
        lines.append(f"### {name}")
        if not has_differences(r):
            lines.append("_All keys match._")
        else:
            for k in sorted(r.missing_in_target or {}):
                lines.append(f"- ❌ `{k}` missing in **target**")
            for k in sorted(r.missing_in_source or {}):
                lines.append(f"- ➕ `{k}` missing in **source**")
            for k, (sv, tv) in sorted((r.mismatched or {}).items()):
                lines.append(f"- ⚠️ `{k}`: `{sv}` → `{tv}`")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_group(grouped: GroupedResult, fmt: str = "text") -> str:
    fmt = fmt.lower()
    if fmt == "json":
        return format_group_json(grouped)
    if fmt in ("md", "markdown"):
        return format_group_markdown(grouped)
    return format_group_text(grouped)
