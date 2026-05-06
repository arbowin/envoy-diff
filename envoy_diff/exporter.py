"""Export diff results to various file formats (CSV, HTML)."""

from __future__ import annotations

import csv
import io
from enum import Enum
from typing import Optional

from envoy_diff.comparator import DiffResult


class ExportFormat(str, Enum):
    CSV = "csv"
    HTML = "html"


class ExportError(Exception):
    """Raised when export fails."""


def export_csv(result: DiffResult) -> str:
    """Render a DiffResult as a CSV string."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "status", "source_value", "target_value"])

    for key in sorted(result.missing_in_target):
        writer.writerow([key, "missing_in_target", result.source.get(key, ""), ""])

    for key in sorted(result.missing_in_source):
        writer.writerow([key, "missing_in_source", "", result.target.get(key, "")])

    for key in sorted(result.mismatched):
        writer.writerow([
            key,
            "mismatched",
            result.source.get(key, ""),
            result.target.get(key, ""),
        ])

    return buf.getvalue()


def export_html(result: DiffResult, title: str = "Env Diff Report") -> str:
    """Render a DiffResult as a minimal HTML table."""
    rows: list[str] = []

    def _row(key: str, status: str, src: Optional[str], tgt: Optional[str]) -> str:
        css = {"missing_in_target": "#ffe0e0", "missing_in_source": "#e0f0ff", "mismatched": "#fff3cd"}
        bg = css.get(status, "#ffffff")
        return (
            f'<tr style="background:{bg}">'  
            f"<td>{key}</td><td>{status}</td>"
            f"<td>{src if src is not None else ''}</td>"
            f"<td>{tgt if tgt is not None else ''}</td></tr>"
        )

    for key in sorted(result.missing_in_target):
        rows.append(_row(key, "missing_in_target", result.source.get(key), None))
    for key in sorted(result.missing_in_source):
        rows.append(_row(key, "missing_in_source", None, result.target.get(key)))
    for key in sorted(result.mismatched):
        rows.append(_row(key, "mismatched", result.source.get(key), result.target.get(key)))

    body = "\n".join(rows) if rows else '<tr><td colspan="4">No differences found.</td></tr>'
    return (
        f"<!DOCTYPE html><html><head><title>{title}</title></head><body>"
        f"<h1>{title}</h1>"
        "<table border='1' cellpadding='6' cellspacing='0'>"
        "<thead><tr><th>Key</th><th>Status</th><th>Source</th><th>Target</th></tr></thead>"
        f"<tbody>{body}</tbody></table></body></html>"
    )


def export_result(result: DiffResult, fmt: ExportFormat) -> str:
    """Dispatch export to the appropriate formatter."""
    if fmt == ExportFormat.CSV:
        return export_csv(result)
    if fmt == ExportFormat.HTML:
        return export_html(result)
    raise ExportError(f"Unsupported export format: {fmt}")
