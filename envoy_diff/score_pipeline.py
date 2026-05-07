"""High-level helper: parse two .env files, diff them, and produce a score report.

This ties together :mod:`envoy_diff.parser`, :mod:`envoy_diff.comparator`,
:mod:`envoy_diff.scorer`, and :mod:`envoy_diff.score_reporter` into a single
convenient call suitable for use from the CLI or external scripts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from envoy_diff.comparator import compare_envs
from envoy_diff.parser import EnvParseError, parse_env_file
from envoy_diff.score_reporter import render_score
from envoy_diff.scorer import ScoreResult, score_diff


class ScorePipelineError(Exception):
    """Raised when the scoring pipeline cannot complete."""


@dataclass(frozen=True)
class ScorePipelineOutput:
    """Result returned by :func:`score_files`."""

    score_result: ScoreResult
    report: str  # pre-rendered string in the requested format


def score_files(
    source: str | Path,
    target: str | Path,
    fmt: str = "text",
    total_keys: Optional[int] = None,
) -> ScorePipelineOutput:
    """Parse *source* and *target* .env files, diff them, and return a score.

    Args:
        source: Path to the source .env file.
        target: Path to the target .env file.
        fmt: Output format – ``'text'``, ``'json'``, or ``'markdown'``.
        total_keys: Optional denominator override passed to :func:`score_diff`.

    Returns:
        A :class:`ScorePipelineOutput` containing the score and rendered report.

    Raises:
        ScorePipelineError: If either file cannot be parsed.
    """
    try:
        src_env = parse_env_file(str(source))
    except (EnvParseError, OSError) as exc:
        raise ScorePipelineError(f"Cannot parse source file {source!r}: {exc}") from exc

    try:
        tgt_env = parse_env_file(str(target))
    except (EnvParseError, OSError) as exc:
        raise ScorePipelineError(f"Cannot parse target file {target!r}: {exc}") from exc

    diff = compare_envs(src_env, tgt_env)
    sr = score_diff(diff, total_keys=total_keys)
    report = render_score(sr, fmt=fmt)

    return ScorePipelineOutput(score_result=sr, report=report)
