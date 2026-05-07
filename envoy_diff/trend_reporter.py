"""Format TrendLog data as text, JSON, or Markdown."""

from __future__ import annotations

import json
from typing import List

from envoy_diff.trend import TrendLog


def _text_lines(log: TrendLog) -> List[str]:
    lines: List[str] = ["Trend Log", "=========="]
    if not log.entries:
        lines.append("No entries recorded.")
        return lines
    for e in log.entries:
        label = f" [{e.label}]" if e.label else ""
        lines.append(
            f"{e.timestamp}{label}  score={e.score:.1f}  grade={e.grade}"
            f"  missing_target={e.missing_in_target}"
            f"  missing_source={e.missing_in_source}"
            f"  mismatched={e.mismatched}"
        )
    delta = log.delta()
    if delta is not None:
        direction = "+" if delta >= 0 else ""
        lines.append(f"\nScore delta (last two entries): {direction}{delta}")
    return lines


def format_trend_text(log: TrendLog) -> str:
    return "\n".join(_text_lines(log))


def format_trend_json(log: TrendLog) -> str:
    payload = {
        "entries": [e.__dict__ for e in log.entries],
        "delta": log.delta(),
    }
    return json.dumps(payload, indent=2)


def format_trend_markdown(log: TrendLog) -> str:
    lines: List[str] = ["# Trend Log", ""]
    if not log.entries:
        lines.append("_No entries recorded._")
        return "\n".join(lines)
    lines.append("| Timestamp | Label | Score | Grade | Missing↓ | Missing↑ | Mismatch |")
    lines.append("|-----------|-------|-------|-------|----------|----------|----------|")
    for e in log.entries:
        label = e.label or ""
        lines.append(
            f"| {e.timestamp} | {label} | {e.score:.1f} | {e.grade}"
            f" | {e.missing_in_target} | {e.missing_in_source} | {e.mismatched} |"
        )
    delta = log.delta()
    if delta is not None:
        direction = "+" if delta >= 0 else ""
        lines.append(f"\n**Score delta:** `{direction}{delta}`")
    return "\n".join(lines)


def render_trend(log: TrendLog, fmt: str = "text") -> str:
    """Render *log* in the requested format (text, json, markdown)."""
    fmt = fmt.lower()
    if fmt == "json":
        return format_trend_json(log)
    if fmt in ("md", "markdown"):
        return format_trend_markdown(log)
    return format_trend_text(log)
