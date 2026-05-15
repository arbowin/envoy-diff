"""Format WatchEvent objects for display."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import List

from envoy_diff.watchdog import WatchEvent
from envoy_diff.formatter import format_result, OutputFormat


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _text_lines(event: WatchEvent) -> List[str]:
    lines: List[str] = [
        f"[{_timestamp()}] Change detected in: {event.path}",
    ]
    diff_text = format_result(event.report.result, OutputFormat.TEXT)
    lines.extend(diff_text.splitlines())
    return lines


def format_watch_text(event: WatchEvent) -> str:
    return "\n".join(_text_lines(event))


def format_watch_json(event: WatchEvent) -> str:
    result = event.report.result
    payload = {
        "timestamp": _timestamp(),
        "path": event.path,
        "missing_in_target": list(result.missing_in_target),
        "missing_in_source": list(result.missing_in_source),
        "mismatched": {
            k: {"source": v[0], "target": v[1]}
            for k, v in result.mismatched.items()
        },
        "has_differences": result.has_differences,
    }
    return json.dumps(payload, indent=2)


def format_watch_markdown(event: WatchEvent) -> str:
    lines: List[str] = [
        f"## Change detected — `{event.path}`",
        f"_Timestamp: {_timestamp()}_",
        "",
    ]
    lines.append(format_result(event.report.result, OutputFormat.MARKDOWN))
    return "\n".join(lines)


def render_watch(event: WatchEvent, fmt: str = "text") -> str:
    """Render a *WatchEvent* in the requested format (text/json/markdown)."""
    fmt = fmt.lower()
    if fmt == "json":
        return format_watch_json(event)
    if fmt == "markdown":
        return format_watch_markdown(event)
    return format_watch_text(event)
