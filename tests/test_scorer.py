"""Tests for envoy_diff.scorer."""

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.scorer import ScoreResult, score_diff


@pytest.fixture()
def perfect_result() -> DiffResult:
    return DiffResult(
        missing_in_target=[],
        missing_in_source=[],
        mismatched={},
        common={"KEY": "value", "OTHER": "123"},
    )


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        missing_in_target=["ALPHA", "BETA"],
        missing_in_source=["GAMMA"],
        mismatched={"DELTA": ("old", "new")},
        common={"SHARED": "same"},
    )


def test_perfect_score_is_100(perfect_result):
    sr = score_diff(perfect_result)
    assert sr.score == 100


def test_perfect_is_flagged(perfect_result):
    sr = score_diff(perfect_result)
    assert sr.is_perfect is True


def test_perfect_grade_is_a(perfect_result):
    sr = score_diff(perfect_result)
    assert sr.grade == "A"


def test_score_below_100_when_differences_exist(diff_result):
    sr = score_diff(diff_result)
    assert sr.score < 100


def test_score_not_negative(diff_result):
    sr = score_diff(diff_result)
    assert sr.score >= 0


def test_breakdown_counts_match(diff_result):
    sr = score_diff(diff_result)
    assert sr.missing_in_target == 2
    assert sr.missing_in_source == 1
    assert sr.mismatched == 1


def test_raw_penalty_is_positive(diff_result):
    sr = score_diff(diff_result)
    assert sr.raw_penalty > 0


def test_custom_total_keys_affects_score(diff_result):
    sr_small = score_diff(diff_result, total_keys=5)
    sr_large = score_diff(diff_result, total_keys=500)
    # Larger denominator means smaller scaled penalty → higher score
    assert sr_large.score >= sr_small.score


def test_grade_f_for_very_bad_result():
    bad = DiffResult(
        missing_in_target=[f"K{i}" for i in range(20)],
        missing_in_source=[],
        mismatched={},
        common={},
    )
    sr = score_diff(bad, total_keys=20)
    assert sr.grade in ("D", "F")


def test_score_result_is_frozen(perfect_result):
    sr = score_diff(perfect_result)
    with pytest.raises((AttributeError, TypeError)):
        sr.score = 0  # type: ignore[misc]
