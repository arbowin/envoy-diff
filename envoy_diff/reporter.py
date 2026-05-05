"""Report generation for env diff results, supporting multiple output destinations."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, TextIO

from envoy_diff.comparator import DiffResult
from envoy_diff.formatter import OutputFormat, format_result


class ReportError(Exception):
    """Raised when a report cannot be written."""


def write_report(
    result: DiffResult,
    fmt: OutputFormat = OutputFormat.TEXT,
    output_path: Optional[Path] = None,
    stream: Optional[TextIO] = None,
) -> None:
    """Write a formatted diff report to a file or stream.

    Priority: output_path > stream > stdout.

    Args:
        result: The diff result to report on.
        fmt: Output format (text, json, markdown).
        output_path: Optional file path to write the report to.
        stream: Optional text stream to write to.

    Raises:
        ReportError: If the output file cannot be written.
    """
    content = format_result(result, fmt)

    if output_path is not None:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise ReportError(f"Failed to write report to {output_path}: {exc}") from exc
        return

    target: TextIO = stream if stream is not None else sys.stdout
    target.write(content)
    if not content.endswith("\n"):
        target.write("\n")


def report_to_string(
    result: DiffResult,
    fmt: OutputFormat = OutputFormat.TEXT,
) -> str:
    """Return the formatted diff report as a string.

    Args:
        result: The diff result to report on.
        fmt: Output format (text, json, markdown).

    Returns:
        Formatted report string.
    """
    return format_result(result, fmt)
