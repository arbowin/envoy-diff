"""Convenience helpers that combine diff_files with snapshot persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from envoy_diff.comparator import DiffResult
from envoy_diff.differ import DiffOptions, DiffReport, diff_files
from envoy_diff.snapshot import SnapshotError, load_snapshot, save_snapshot


def diff_and_snapshot(
    source: Union[str, Path],
    target: Union[str, Path],
    snapshot_path: Union[str, Path],
    options: Optional[DiffOptions] = None,
) -> DiffReport:
    """Run a diff and persist the result as a snapshot.

    Returns the full DiffReport; the snapshot is written as a side-effect.
    """
    report = diff_files(source, target, options=options)
    save_snapshot(report.result, snapshot_path)
    return report


def diff_against_snapshot(
    source: Union[str, Path],
    snapshot_path: Union[str, Path],
    options: Optional[DiffOptions] = None,
) -> DiffReport:
    """Diff a live .env file against a previously saved snapshot.

    The snapshot is treated as the *target*; the live file is the *source*.
    Raises SnapshotError if the snapshot cannot be loaded.
    """
    baseline: DiffResult = load_snapshot(snapshot_path)
    # Reconstruct a temporary target mapping from the snapshot data.
    target_env: dict[str, Optional[str]] = {}
    for key in baseline.missing_in_target:
        pass  # key existed only in source at snapshot time — skip
    for key in baseline.missing_in_source:
        target_env[key] = None
    for key, (_, tval) in baseline.mismatched.items():
        target_env[key] = tval
    for key in baseline.common:
        target_env[key] = None  # value unknown; treat as present

    report = diff_files(source, snapshot_path, options=options)
    return report
