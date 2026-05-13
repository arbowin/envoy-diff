"""Render a :class:`SummaryStats` in text, JSON, or Markdown."""

from __future__ import annotations

import json
from typing import List

from envoy_diff.summarizer import SummaryStats


def _text_lines(stats: SummaryStats) -> List[str]:
    lines = [
        "=== Diff Summary ===",
        stats.headline(),
        "",
        f"  Total keys      : {stats.total_keys}",
        f"  Matching        : {stats.matching}",
        f"  Missing target  : {stats.missing_in_target}",
        f"  Missing source  : {stats.missing_in_source}",
        f"  Mismatched      : {stats.mismatched}",
        f"  Drift           : {stats.drift_percent}%",
    ]
    return lines


def format_summary_text(stats: SummaryStats) -> str:
    """Return a plain-text summary report."""
    return "\n".join(_text_lines(stats))


def format_summary_json(stats: SummaryStats) -> str:
    """Return a JSON summary report."""
    data = {
        "total_keys": stats.total_keys,
        "matching": stats.matching,
        "missing_in_target": stats.missing_in_target,
        "missing_in_source": stats.missing_in_source,
        "mismatched": stats.mismatched,
        "drift_percent": stats.drift_percent,
        "headline": stats.headline(),
    }
    return json.dumps(data, indent=2)


def format_summary_markdown(stats: SummaryStats) -> str:
    """Return a Markdown summary report."""
    lines = [
        "## Diff Summary",
        "",
        f"_{stats.headline()}_",
        "",
        "| Metric | Count |",
        "|---|---|",
        f"| Total keys | {stats.total_keys} |",
        f"| Matching | {stats.matching} |",
        f"| Missing in target | {stats.missing_in_target} |",
        f"| Missing in source | {stats.missing_in_source} |",
        f"| Mismatched | {stats.mismatched} |",
        f"| Drift | {stats.drift_percent}% |",
    ]
    return "\n".join(lines)


def render_summary(stats: SummaryStats, fmt: str = "text") -> str:
    """Dispatch to the appropriate formatter based on *fmt*."""
    fmt = fmt.lower()
    if fmt == "json":
        return format_summary_json(stats)
    if fmt in ("md", "markdown"):
        return format_summary_markdown(stats)
    return format_summary_text(stats)
