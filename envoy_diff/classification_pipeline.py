"""End-to-end pipeline: parse two env files, diff, then classify."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from envoy_diff.classifier import ClassifiedResult, classify_result
from envoy_diff.classification_reporter import render_classification
from envoy_diff.comparator import compare_envs
from envoy_diff.parser import parse_env_file, EnvParseError


class ClassificationPipelineError(Exception):
    """Raised when the classification pipeline cannot complete."""


@dataclass
class ClassificationPipelineOutput:
    classified: ClassifiedResult
    rendered: str


def run_classification_pipeline(
    source_path: str | Path,
    target_path: str | Path,
    fmt: str = "text",
) -> ClassificationPipelineOutput:
    """Parse *source_path* and *target_path*, diff them, then classify.

    Args:
        source_path: Path to the source .env file.
        target_path: Path to the target .env file.
        fmt: Output format – ``"text"``, ``"json"``, or ``"markdown"``.

    Returns:
        A :class:`ClassificationPipelineOutput` holding the structured result
        and a pre-rendered string.

    Raises:
        ClassificationPipelineError: On any parse or I/O failure.
    """
    try:
        source_env = parse_env_file(str(source_path))
        target_env = parse_env_file(str(target_path))
    except (EnvParseError, OSError) as exc:
        raise ClassificationPipelineError(str(exc)) from exc

    diff = compare_envs(
        source_env,
        target_env,
        source_path=str(source_path),
        target_path=str(target_path),
    )
    classified = classify_result(diff)
    rendered = render_classification(classified, fmt=fmt)
    return ClassificationPipelineOutput(classified=classified, rendered=rendered)
