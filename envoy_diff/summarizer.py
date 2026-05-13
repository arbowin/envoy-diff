"""Summarizer: produce a concise human-readable summary of a DiffResult."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from envoy_diff.comparator import DiffResult


@dataclass
class SummaryStats:
    """Aggregated statistics derived from a DiffResult."""

    total_keys: int
    missing_in_target: int
    missing_in_source: int
    mismatched: int
    matching: int

    @property
    def drift_ratio(self) -> float:
        """Fraction of keys that differ (0.0 – 1.0)."""
        if self.total_keys == 0:
            return 0.0
        differing = self.missing_in_target + self.missing_in_source + self.mismatched
        return differing / self.total_keys

    @property
    def drift_percent(self) -> float:
        """Drift expressed as a percentage."""
        return round(self.drift_ratio * 100, 2)

    def headline(self) -> str:
        """Return a one-line headline string."""
        if self.total_keys == 0:
            return "No keys found in either environment."
        if self.mismatched == 0 and self.missing_in_target == 0 and self.missing_in_source == 0:
            return f"Environments are in sync ({self.total_keys} keys)."
        parts: List[str] = []
        if self.missing_in_target:
            parts.append(f"{self.missing_in_target} missing in target")
        if self.missing_in_source:
            parts.append(f"{self.missing_in_source} missing in source")
        if self.mismatched:
            parts.append(f"{self.mismatched} mismatched")
        return ", ".join(parts) + f" (drift {self.drift_percent}%)."


def summarize(result: DiffResult) -> SummaryStats:
    """Build a :class:`SummaryStats` from *result*."""
    all_keys = set(result.missing_in_target) | set(result.missing_in_source) | set(result.mismatched) | set(result.matching)
    total = len(all_keys)
    return SummaryStats(
        total_keys=total,
        missing_in_target=len(result.missing_in_target),
        missing_in_source=len(result.missing_in_source),
        mismatched=len(result.mismatched),
        matching=len(result.matching),
    )
