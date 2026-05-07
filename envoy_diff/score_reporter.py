"""Render a :class:`ScoreResult` in text, JSON, or Markdown."""

import json
from typing import List

from envoy_diff.scorer import ScoreResult


def _text_lines(result: ScoreResult) -> List[str]:
    lines = [
        f"Health Score : {result.score}/100  (Grade: {result.grade})",
        f"Total keys   : {result.total_keys}",
        f"Missing (target): {result.missing_in_target}",
        f"Missing (source): {result.missing_in_source}",
        f"Mismatched      : {result.mismatched}",
        f"Raw penalty     : {result.raw_penalty}",
    ]
    if result.is_perfect:
        lines.append("✓ Environments are in perfect sync.")
    return lines


def format_score_text(result: ScoreResult) -> str:
    """Return a plain-text report for *result*."""
    return "\n".join(_text_lines(result))


def format_score_json(result: ScoreResult) -> str:
    """Return a JSON string for *result*."""
    payload = {
        "score": result.score,
        "grade": result.grade,
        "is_perfect": result.is_perfect,
        "total_keys": result.total_keys,
        "missing_in_target": result.missing_in_target,
        "missing_in_source": result.missing_in_source,
        "mismatched": result.mismatched,
        "raw_penalty": result.raw_penalty,
    }
    return json.dumps(payload, indent=2)


def format_score_markdown(result: ScoreResult) -> str:
    """Return a Markdown report for *result*."""
    lines = [
        "## Env Health Score",
        "",
        f"| Metric | Value |",
        "|--------|-------|" ,
        f"| Score | **{result.score}/100** |",
        f"| Grade | **{result.grade}** |",
        f"| Total keys | {result.total_keys} |",
        f"| Missing in target | {result.missing_in_target} |",
        f"| Missing in source | {result.missing_in_source} |",
        f"| Mismatched | {result.mismatched} |",
        f"| Raw penalty | {result.raw_penalty} |",
    ]
    if result.is_perfect:
        lines.append("")
        lines.append("_✓ Environments are in perfect sync._")
    return "\n".join(lines)


def render_score(result: ScoreResult, fmt: str = "text") -> str:
    """Dispatch to the correct formatter.

    Args:
        result: Score result to render.
        fmt: One of ``'text'``, ``'json'``, or ``'markdown'``.

    Raises:
        ValueError: If *fmt* is not recognised.
    """
    fmt = fmt.lower()
    if fmt == "text":
        return format_score_text(result)
    if fmt == "json":
        return format_score_json(result)
    if fmt in ("markdown", "md"):
        return format_score_markdown(result)
    raise ValueError(f"Unknown format: {fmt!r}. Choose 'text', 'json', or 'markdown'.")
