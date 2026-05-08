"""High-level pipeline: diff two env files and compare against a baseline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from envoy_diff.baseline import (
    BaselineComparison,
    BaselineError,
    compare_against_baseline,
    load_baseline,
    save_baseline,
)
from envoy_diff.differ import DiffOptions, diff_files
from envoy_diff.comparator import DiffResult


@dataclass
class BaselinePipelineOutput:
    current: DiffResult
    comparison: Optional[BaselineComparison]
    baseline_path: Path
    baseline_created: bool


def run_baseline_pipeline(
    source: str | Path,
    target: str | Path,
    baseline_path: str | Path,
    *,
    create_if_missing: bool = True,
    options: Optional[DiffOptions] = None,
) -> BaselinePipelineOutput:
    """Diff *source* vs *target* and compare the result against a saved baseline.

    If no baseline exists and *create_if_missing* is True, the current result
    is saved as the new baseline and ``comparison`` is ``None``.
    """
    opts = options or DiffOptions()
    report = diff_files(str(source), str(target), opts)
    current = report.result

    dest = Path(baseline_path)
    created = False
    comparison: Optional[BaselineComparison] = None

    if dest.exists():
        baseline = load_baseline(dest)
        comparison = compare_against_baseline(current, baseline)
    elif create_if_missing:
        save_baseline(current, dest)
        created = True
    else:
        raise BaselineError(f"No baseline found at {dest} and create_if_missing=False")

    return BaselinePipelineOutput(
        current=current,
        comparison=comparison,
        baseline_path=dest,
        baseline_created=created,
    )
