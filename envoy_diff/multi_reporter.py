"""Format a MultiDiffReport as text, JSON, or Markdown."""

from __future__ import annotations

import json
from typing import List

from .differ_multi import MultiDiffReport
from .formatter import format_result, OutputFormat


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _text_lines(report: MultiDiffReport) -> List[str]:
    lines: List[str] = [
        f"Multi-diff  source: {report.source}",
        f"Targets    : {len(report.targets())}",
        "",
    ]
    for label in report.targets():
        sub = report.get(label)
        assert sub is not None
        lines.append(f"--- {label} ({sub.target}) ---")
        lines.extend(format_result(sub.result, OutputFormat.TEXT).splitlines())
        lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Public formatters
# ---------------------------------------------------------------------------

def format_multi_text(report: MultiDiffReport) -> str:
    """Return a plain-text representation of the multi-diff report."""
    return "\n".join(_text_lines(report))


def format_multi_json(report: MultiDiffReport) -> str:
    """Return a JSON representation of the multi-diff report."""
    payload = {
        "source": str(report.source),
        "targets": {
            label: json.loads(format_result(r.result, OutputFormat.JSON))
            for label, r in report.reports.items()
        },
    }
    return json.dumps(payload, indent=2)


def format_multi_markdown(report: MultiDiffReport) -> str:
    """Return a Markdown representation of the multi-diff report."""
    lines: List[str] = [
        f"# Multi-diff Report",
        f"",
        f"**Source:** `{report.source}`  ",
        f"**Targets:** {len(report.targets())}",
        "",
    ]
    for label in report.targets():
        sub = report.get(label)
        assert sub is not None
        lines.append(f"## {label}")
        lines.append(f"*Path: `{sub.target}`*")
        lines.append("")
        lines.extend(format_result(sub.result, OutputFormat.MARKDOWN).splitlines())
        lines.append("")
    return "\n".join(lines)


def render_multi(report: MultiDiffReport, fmt: str = "text") -> str:
    """Render *report* using the named format (text / json / markdown)."""
    fmt = fmt.lower()
    if fmt == "json":
        return format_multi_json(report)
    if fmt in ("md", "markdown"):
        return format_multi_markdown(report)
    return format_multi_text(report)
