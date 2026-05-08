"""Format BaselineComparison results as text, JSON, or Markdown."""

from __future__ import annotations

import json

from envoy_diff.baseline import BaselineComparison


def _text_lines(cmp: BaselineComparison) -> list[str]:
    lines: list[str] = ["=== Baseline Comparison ==="]
    if not cmp.has_regressions and not cmp.has_improvements:
        lines.append("No changes from baseline.")
        return lines
    if cmp.has_regressions:
        lines.append(f"New issues ({len(cmp.new_keys)}):")
        for k in cmp.new_keys:
            lines.append(f"  + {k}")
    if cmp.has_improvements:
        lines.append(f"Resolved issues ({len(cmp.resolved_keys)}):")
        for k in cmp.resolved_keys:
            lines.append(f"  - {k}")
    if cmp.unchanged_keys:
        lines.append(f"Unchanged issues: {len(cmp.unchanged_keys)}")
    return lines


def format_baseline_text(cmp: BaselineComparison) -> str:
    return "\n".join(_text_lines(cmp))


def format_baseline_json(cmp: BaselineComparison) -> str:
    payload = {
        "new_keys": cmp.new_keys,
        "resolved_keys": cmp.resolved_keys,
        "unchanged_keys": cmp.unchanged_keys,
        "has_regressions": cmp.has_regressions,
        "has_improvements": cmp.has_improvements,
    }
    return json.dumps(payload, indent=2)


def format_baseline_markdown(cmp: BaselineComparison) -> str:
    lines = ["## Baseline Comparison"]
    if not cmp.has_regressions and not cmp.has_improvements:
        lines.append("_No changes from baseline._")
        return "\n".join(lines)
    if cmp.has_regressions:
        lines.append(f"### New Issues ({len(cmp.new_keys)})")
        for k in cmp.new_keys:
            lines.append(f"- `{k}`")
    if cmp.has_improvements:
        lines.append(f"### Resolved Issues ({len(cmp.resolved_keys)})")
        for k in cmp.resolved_keys:
            lines.append(f"- `{k}`")
    if cmp.unchanged_keys:
        lines.append(f"### Unchanged Issues: {len(cmp.unchanged_keys)}")
    return "\n".join(lines)


def render_baseline(cmp: BaselineComparison, fmt: str = "text") -> str:
    """Render *cmp* in the requested format (text/json/markdown)."""
    fmt = fmt.lower()
    if fmt == "json":
        return format_baseline_json(cmp)
    if fmt in ("markdown", "md"):
        return format_baseline_markdown(cmp)
    return format_baseline_text(cmp)
