"""Multi-file diff: compare one source .env against multiple target .env files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .comparator import DiffResult
from .differ import DiffOptions, DiffReport, diff_files


class MultiDiffError(Exception):
    """Raised when a multi-file diff cannot be completed."""


@dataclass
class MultiDiffReport:
    """Holds per-target diff reports for a single source file."""

    source: Path
    reports: Dict[str, DiffReport] = field(default_factory=dict)

    # ------------------------------------------------------------------
    def targets(self) -> List[str]:
        """Return the target labels in insertion order."""
        return list(self.reports.keys())

    def get(self, label: str) -> Optional[DiffReport]:
        """Return the DiffReport for *label*, or None if absent."""
        return self.reports.get(label)

    def all_clean(self) -> bool:
        """True only when every target is identical to the source."""
        return all(not r.result.has_differences() for r in self.reports.values())

    def results(self) -> Dict[str, DiffResult]:
        """Convenience: return {label: DiffResult} mapping."""
        return {label: r.result for label, r in self.reports.items()}


def diff_multi(
    source: Path,
    targets: Dict[str, Path],
    options: Optional[DiffOptions] = None,
) -> MultiDiffReport:
    """Diff *source* against each path in *targets*.

    Parameters
    ----------
    source:
        The reference .env file.
    targets:
        Mapping of human-readable label -> path to compare against source.
    options:
        Shared DiffOptions applied to every pair; defaults to DiffOptions().

    Returns
    -------
    MultiDiffReport
        A report containing one DiffReport per target label.

    Raises
    ------
    MultiDiffError
        If *targets* is empty or if any individual diff raises.
    """
    if not targets:
        raise MultiDiffError("At least one target file must be provided.")

    opts = options or DiffOptions()
    report = MultiDiffReport(source=source)

    for label, target_path in targets.items():
        try:
            report.reports[label] = diff_files(source, target_path, opts)
        except Exception as exc:  # pragma: no cover
            raise MultiDiffError(
                f"Failed to diff '{source}' against '{target_path}' ({label}): {exc}"
            ) from exc

    return report
