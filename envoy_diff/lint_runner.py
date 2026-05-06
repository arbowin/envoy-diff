"""High-level runner that lints multiple .env files and aggregates results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .linter import LintResult, LintSeverity, lint_env_file


@dataclass
class LintRunReport:
    """Aggregated lint results for one or more files."""
    results: Dict[str, LintResult] = field(default_factory=dict)

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results.values())

    @property
    def total_errors(self) -> int:
        return sum(len(r.errors) for r in self.results.values())

    @property
    def total_warnings(self) -> int:
        return sum(len(r.warnings) for r in self.results.values())

    def summary_lines(self) -> List[str]:
        lines: List[str] = []
        for path, result in self.results.items():
            status = "PASS" if result.passed else "FAIL"
            lines.append(f"{status}  {path}  (errors={len(result.errors)}, warnings={len(result.warnings)})")
            for issue in result.issues:
                lines.append(f"  {issue}")
        return lines

    def summary(self) -> str:
        return "\n".join(self.summary_lines())


class LintRunError(Exception):
    """Raised when a file cannot be opened for linting."""


def run_lint(
    paths: List[str],
    min_severity: Optional[LintSeverity] = None,
) -> LintRunReport:
    """Lint each file in *paths* and return an aggregated report.

    Args:
        paths: File paths to lint.
        min_severity: If given, only issues at this severity or above are
            retained (ERROR > WARNING > INFO).

    Raises:
        LintRunError: If any file cannot be read.
    """
    _order = [LintSeverity.INFO, LintSeverity.WARNING, LintSeverity.ERROR]
    report = LintRunReport()

    for path in paths:
        try:
            result = lint_env_file(path)
        except OSError as exc:
            raise LintRunError(f"Cannot read '{path}': {exc}") from exc

        if min_severity is not None:
            threshold = _order.index(min_severity)
            result.issues = [i for i in result.issues if _order.index(i.severity) >= threshold]

        report.results[path] = result

    return report
