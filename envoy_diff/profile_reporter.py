"""Format and render ProfileResult objects for human consumption."""
from __future__ import annotations

import json
from typing import List

from envoy_diff.profiler import ProfileResult


def _text_lines(result: ProfileResult) -> List[str]:
    lines = [
        f"File : {result.path}",
        f"Total keys      : {result.total_keys}",
        f"Non-empty values: {result.non_empty_values}",
        f"Empty values    : {result.empty_values}",
        f"Empty ratio     : {result.empty_ratio:.1%}",
        f"Longest key     : {result.longest_key or '—'}",
        f"Longest value in: {result.longest_value_key or '—'}",
    ]
    if result.unique_prefixes:
        lines.append("Prefixes        : " + ", ".join(result.unique_prefixes))
    else:
        lines.append("Prefixes        : —")
    if result.duplicate_keys:
        lines.append("Duplicate keys  : " + ", ".join(result.duplicate_keys))
    return lines


def format_profile_text(result: ProfileResult) -> str:
    """Return a plain-text summary of *result*."""
    return "\n".join(_text_lines(result))


def format_profile_json(result: ProfileResult) -> str:
    """Return a JSON representation of *result*."""
    data = {
        "path": result.path,
        "total_keys": result.total_keys,
        "non_empty_values": result.non_empty_values,
        "empty_values": result.empty_values,
        "empty_ratio": round(result.empty_ratio, 4),
        "longest_key": result.longest_key,
        "longest_value_key": result.longest_value_key,
        "unique_prefixes": result.unique_prefixes,
        "duplicate_keys": result.duplicate_keys,
    }
    return json.dumps(data, indent=2)


def format_profile_markdown(result: ProfileResult) -> str:
    """Return a Markdown summary table for *result*."""
    rows = [
        ("File", result.path),
        ("Total keys", str(result.total_keys)),
        ("Non-empty values", str(result.non_empty_values)),
        ("Empty values", str(result.empty_values)),
        ("Empty ratio", f"{result.empty_ratio:.1%}"),
        ("Longest key", result.longest_key or "—"),
        ("Longest value in", result.longest_value_key or "—"),
        ("Prefixes", ", ".join(result.unique_prefixes) or "—"),
    ]
    if result.duplicate_keys:
        rows.append(("Duplicate keys", ", ".join(result.duplicate_keys)))

    header = "| Metric | Value |"
    separator = "|--------|-------|"
    body = [f"| {k} | {v} |" for k, v in rows]
    return "\n".join([header, separator] + body)


def render_profile(
    result: ProfileResult,
    fmt: str = "text",
) -> str:
    """Dispatch to the appropriate formatter.

    Parameters
    ----------
    result:
        The profile to render.
    fmt:
        One of ``'text'``, ``'json'``, or ``'markdown'``.

    Raises
    ------
    ValueError
        If *fmt* is not recognised.
    """
    if fmt == "text":
        return format_profile_text(result)
    if fmt == "json":
        return format_profile_json(result)
    if fmt == "markdown":
        return format_profile_markdown(result)
    raise ValueError(f"Unknown profile format: '{fmt}'. Choose text, json, or markdown.")
