"""Write exported content to files or stdout."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from envoy_diff.comparator import DiffResult
from envoy_diff.exporter import ExportFormat, ExportError, export_result


class WriterError(Exception):
    """Raised when writing exported output fails."""


def write_export(
    result: DiffResult,
    fmt: ExportFormat,
    output_path: Optional[Path] = None,
    encoding: str = "utf-8",
) -> None:
    """Export *result* in *fmt* and write to *output_path* or stdout.

    Args:
        result: The diff result to export.
        fmt: Target export format.
        output_path: Destination file; if None, writes to stdout.
        encoding: File encoding (ignored when writing to stdout).

    Raises:
        WriterError: If the file cannot be written.
    """
    try:
        content = export_result(result, fmt)
    except ExportError as exc:
        raise WriterError(str(exc)) from exc

    if output_path is None:
        sys.stdout.write(content)
        return

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding=encoding)
    except OSError as exc:
        raise WriterError(f"Cannot write to {output_path}: {exc}") from exc


def export_to_string(
    result: DiffResult,
    fmt: ExportFormat,
) -> str:
    """Return exported content as a string without writing anywhere."""
    try:
        return export_result(result, fmt)
    except ExportError as exc:
        raise WriterError(str(exc)) from exc
