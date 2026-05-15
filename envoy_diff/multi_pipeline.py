"""High-level pipeline: diff one source against many targets and render output."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from .differ import DiffOptions
from .differ_multi import MultiDiffReport, MultiDiffError, diff_multi
from .multi_reporter import render_multi


class MultiPipelineError(Exception):
    """Raised when the multi-file pipeline cannot complete."""


@dataclass
class MultiPipelineOutput:
    """Result returned by :func:`run_multi_pipeline`."""

    report: MultiDiffReport
    rendered: str
    all_clean: bool


def run_multi_pipeline(
    source: Path,
    targets: Dict[str, Path],
    fmt: str = "text",
    options: Optional[DiffOptions] = None,
) -> MultiPipelineOutput:
    """Run a full multi-target diff and return rendered output.

    Parameters
    ----------
    source:
        Reference .env file path.
    targets:
        Label -> path mapping of files to compare against *source*.
    fmt:
        Output format: ``"text"``, ``"json"``, or ``"markdown"``.
    options:
        Optional DiffOptions forwarded to each individual diff.

    Returns
    -------
    MultiPipelineOutput

    Raises
    ------
    MultiPipelineError
        Wraps any underlying error so callers get a single exception type.
    """
    try:
        report = diff_multi(source, targets, options)
    except MultiDiffError as exc:
        raise MultiPipelineError(str(exc)) from exc

    rendered = render_multi(report, fmt=fmt)
    return MultiPipelineOutput(
        report=report,
        rendered=rendered,
        all_clean=report.all_clean(),
    )
