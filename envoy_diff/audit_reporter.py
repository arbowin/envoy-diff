"""Format audit logs for human-readable output."""

from __future__ import annotations

import json
from typing import List

from envoy_diff.auditor import AuditEntry, AuditLog
from envoy_diff.comparator import has_differences


def _status_label(entry: AuditEntry) -> str:
    return "DIFF" if has_differences(entry.result) else "CLEAN"


def _text_lines(entry: AuditEntry) -> List[str]:
    lines = [
        f"[{entry.timestamp}] {_status_label(entry)}",
        f"  source : {entry.source_path}",
        f"  target : {entry.target_path}",
    ]
    r = entry.result
    if r.missing_in_target:
        lines.append(f"  missing in target : {', '.join(sorted(r.missing_in_target))}")
    if r.missing_in_source:
        lines.append(f"  missing in source : {', '.join(sorted(r.missing_in_source))}")
    if r.mismatched:
        lines.append(f"  mismatched keys   : {', '.join(sorted(r.mismatched))}")
    if entry.note:
        lines.append(f"  note   : {entry.note}")
    return lines


def format_audit_text(log: AuditLog) -> str:
    """Render an audit log as plain text."""
    if not log.entries:
        return "No audit entries recorded."
    sections = []
    for entry in log.entries:
        sections.append("\n".join(_text_lines(entry)))
    return "\n\n".join(sections)


def format_audit_json(log: AuditLog) -> str:
    """Render an audit log as JSON."""
    records = []
    for e in log.entries:
        r = e.result
        records.append({
            "timestamp": e.timestamp,
            "source_path": e.source_path,
            "target_path": e.target_path,
            "status": _status_label(e),
            "missing_in_target": sorted(r.missing_in_target),
            "missing_in_source": sorted(r.missing_in_source),
            "mismatched": sorted(r.mismatched),
            "note": e.note,
        })
    return json.dumps(records, indent=2)


def format_audit_markdown(log: AuditLog) -> str:
    """Render an audit log as a Markdown table."""
    if not log.entries:
        return "_No audit entries recorded._"
    lines = [
        "| Timestamp | Status | Source | Target | Note |",
        "| --- | --- | --- | --- | --- |",
    ]
    for e in log.entries:
        note = e.note or ""
        lines.append(
            f"| {e.timestamp} | {_status_label(e)} "
            f"| {e.source_path} | {e.target_path} | {note} |"
        )
    return "\n".join(lines)


def render_audit(log: AuditLog, fmt: str = "text") -> str:
    """Dispatch to the appropriate formatter."""
    fmt = fmt.lower()
    if fmt == "json":
        return format_audit_json(log)
    if fmt in ("md", "markdown"):
        return format_audit_markdown(log)
    return format_audit_text(log)
