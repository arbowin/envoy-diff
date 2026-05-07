"""Scoring module: assigns a numeric health score to a DiffResult.

Score ranges from 0 (worst) to 100 (perfect match).
Penalties are applied for missing keys and mismatched values.
"""

from dataclasses import dataclass
from typing import Optional

from envoy_diff.comparator import DiffResult


# Penalty weights (points deducted per occurrence)
_PENALTY_MISSING_IN_TARGET = 5
_PENALTY_MISSING_IN_SOURCE = 3
_PENALTY_MISMATCH = 2


@dataclass(frozen=True)
class ScoreResult:
    """Holds the computed health score and a breakdown of penalties."""

    score: int  # 0-100
    total_keys: int
    missing_in_target: int
    missing_in_source: int
    mismatched: int
    raw_penalty: int

    @property
    def grade(self) -> str:
        """Letter grade based on score."""
        if self.score >= 90:
            return "A"
        if self.score >= 75:
            return "B"
        if self.score >= 60:
            return "C"
        if self.score >= 40:
            return "D"
        return "F"

    @property
    def is_perfect(self) -> bool:
        return self.score == 100


def score_diff(result: DiffResult, total_keys: Optional[int] = None) -> ScoreResult:
    """Compute a health score for *result*.

    Args:
        result: The diff result to score.
        total_keys: Override for the denominator used in penalty scaling.
                    Defaults to the number of unique keys seen across both sides.

    Returns:
        A :class:`ScoreResult` with the computed score and breakdown.
    """
    n_missing_target = len(result.missing_in_target)
    n_missing_source = len(result.missing_in_source)
    n_mismatch = len(result.mismatched)

    all_keys = (
        set(result.missing_in_target)
        | set(result.missing_in_source)
        | set(result.mismatched)
        | set(result.common)
    )
    denominator = total_keys if total_keys and total_keys > 0 else max(len(all_keys), 1)

    raw_penalty = (
        n_missing_target * _PENALTY_MISSING_IN_TARGET
        + n_missing_source * _PENALTY_MISSING_IN_SOURCE
        + n_mismatch * _PENALTY_MISMATCH
    )

    # Scale penalty relative to the number of keys so larger envs aren't unfairly punished
    scaled_penalty = int((raw_penalty / denominator) * 10)
    score = max(0, 100 - scaled_penalty)

    return ScoreResult(
        score=score,
        total_keys=denominator,
        missing_in_target=n_missing_target,
        missing_in_source=n_missing_source,
        mismatched=n_mismatch,
        raw_penalty=raw_penalty,
    )
