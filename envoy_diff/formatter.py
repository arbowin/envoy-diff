"""Output formatters for env diff results."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envoy_diff.comparator import DiffResult


class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"


def format_text(result: "DiffResult", source_name: str = "source", target_name: str = "target") -> str:
    """Format diff result as human-readable text."""
    lines: list[str] = []

    if result.missing_in_target:
        lines.append(f"Missing in {target_name}:")
        for key in sorted(result.missing_in_target):
            lines.append(f"  - {key}")

    if result.missing_in_source:
        lines.append(f"Missing in {source_name}:")
        for key in sorted(result.missing_in_source):
            lines.append(f"  + {key}")

    if result.mismatched_values:
        lines.append("Mismatched values:")
        for key in sorted(result.mismatched_values):
            src_val, tgt_val = result.mismatched_values[key]
            lines.append(f"  ~ {key}")
            lines.append(f"      {source_name}: {src_val!r}")
            lines.append(f"      {target_name}: {tgt_val!r}")

    if not lines:
        lines.append("No differences found.")

    return "\n".join(lines)


def format_json(result: "DiffResult", source_name: str = "source", target_name: str = "target") -> str:
    """Format diff result as JSON."""
    import json

    data = {
        f"missing_in_{target_name}": sorted(result.missing_in_target),
        f"missing_in_{source_name}": sorted(result.missing_in_source),
        "mismatched_values": {
            key: {source_name: src, target_name: tgt}
            for key, (src, tgt) in sorted(result.mismatched_values.items())
        },
    }
    return json.dumps(data, indent=2)


def format_markdown(result: "DiffResult", source_name: str = "source", target_name: str = "target") -> str:
    """Format diff result as a Markdown table/report."""
    lines: list[str] = ["# Env Diff Report", ""]

    if not (result.missing_in_target or result.missing_in_source or result.mismatched_values):
        lines.append("✅ No differences found.")
        return "\n".join(lines)

    if result.missing_in_target:
        lines.append(f"## Missing in `{target_name}`")
        for key in sorted(result.missing_in_target):
            lines.append(f"- `{key}`")
        lines.append("")

    if result.missing_in_source:
        lines.append(f"## Missing in `{source_name}`")
        for key in sorted(result.missing_in_source):
            lines.append(f"- `{key}`")
        lines.append("")

    if result.mismatched_values:
        lines.append("## Mismatched Values")
        lines.append(f"| Key | `{source_name}` | `{target_name}` |")
        lines.append("|-----|--------|--------|")
        for key in sorted(result.mismatched_values):
            src_val, tgt_val = result.mismatched_values[key]
            lines.append(f"| `{key}` | `{src_val}` | `{tgt_val}` |")
        lines.append("")

    return "\n".join(lines)


def format_result(
    result: "DiffResult",
    fmt: OutputFormat = OutputFormat.TEXT,
    source_name: str = "source",
    target_name: str = "target",
) -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == OutputFormat.JSON:
        return format_json(result, source_name, target_name)
    if fmt == OutputFormat.MARKDOWN:
        return format_markdown(result, source_name, target_name)
    return format_text(result, source_name, target_name)
