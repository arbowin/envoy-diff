"""Tests for envoy_diff.baseline."""

import json
from pathlib import Path

import pytest

from envoy_diff.baseline import (
    BaselineComparison,
    BaselineError,
    compare_against_baseline,
    load_baseline,
    save_baseline,
)
from envoy_diff.comparator import DiffResult


@pytest.fixture()
def clean_result() -> DiffResult:
    return DiffResult(differences=[], source_keys=[], target_keys=[])


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        differences=[
            ("DB_HOST", "missing_in_target", "localhost", None),
            ("API_KEY", "mismatch", "old", "new"),
        ],
        source_keys=["DB_HOST", "API_KEY"],
        target_keys=["API_KEY"],
    )


def test_save_and_load_round_trip(tmp_path: Path, diff_result: DiffResult) -> None:
    p = tmp_path / "baseline.json"
    save_baseline(diff_result, p)
    loaded = load_baseline(p)
    assert {e[0] for e in loaded.differences} == {"DB_HOST", "API_KEY"}


def test_save_creates_valid_json(tmp_path: Path, diff_result: DiffResult) -> None:
    p = tmp_path / "baseline.json"
    save_baseline(diff_result, p)
    data = json.loads(p.read_text())
    assert "differences" in data


def test_load_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(BaselineError, match="not found"):
        load_baseline(tmp_path / "nope.json")


def test_load_invalid_json_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("not json")
    with pytest.raises(BaselineError):
        load_baseline(p)


def test_compare_no_change(diff_result: DiffResult) -> None:
    cmp = compare_against_baseline(diff_result, diff_result)
    assert cmp.new_keys == []
    assert cmp.resolved_keys == []
    assert not cmp.has_regressions
    assert not cmp.has_improvements


def test_compare_new_key(diff_result: DiffResult, clean_result: DiffResult) -> None:
    cmp = compare_against_baseline(diff_result, clean_result)
    assert set(cmp.new_keys) == {"DB_HOST", "API_KEY"}
    assert cmp.has_regressions


def test_compare_resolved_key(diff_result: DiffResult, clean_result: DiffResult) -> None:
    cmp = compare_against_baseline(clean_result, diff_result)
    assert set(cmp.resolved_keys) == {"DB_HOST", "API_KEY"}
    assert cmp.has_improvements


def test_unchanged_keys_tracked(diff_result: DiffResult) -> None:
    extra = DiffResult(
        differences=[
            ("DB_HOST", "missing_in_target", "localhost", None),
            ("NEW_KEY", "mismatch", "a", "b"),
        ],
        source_keys=["DB_HOST", "NEW_KEY"],
        target_keys=["NEW_KEY"],
    )
    cmp = compare_against_baseline(extra, diff_result)
    assert "DB_HOST" in cmp.unchanged_keys
