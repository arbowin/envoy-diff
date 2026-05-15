"""Tests for envoy_diff.splitter."""

from __future__ import annotations

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.splitter import (
    SplitterError,
    SplitResult,
    split_result,
)


@pytest.fixture()
def mixed_result() -> DiffResult:
    return {
        "DB_HOST": ("localhost", "prod-db"),
        "DB_PORT": ("5432", "5432"),
        "APP_DEBUG": ("true", None),
        "APP_SECRET": (None, "s3cr3t"),
        "AWS_REGION": ("us-east-1", "eu-west-1"),
        "UNRELATED": ("foo", "bar"),
    }


def test_split_by_prefix_creates_slices(mixed_result):
    rules = {"database": "DB_", "app": "APP_", "cloud": "AWS_"}
    sr = split_result(mixed_result, rules)
    assert isinstance(sr, SplitResult)
    assert sr.slice_names == ["database", "app", "cloud"]


def test_db_slice_contains_db_keys(mixed_result):
    rules = {"database": "DB_", "app": "APP_"}
    sr = split_result(mixed_result, rules)
    db = sr.get("database")
    assert db is not None
    assert set(db.result.keys()) == {"DB_HOST", "DB_PORT"}


def test_app_slice_contains_app_keys(mixed_result):
    rules = {"database": "DB_", "app": "APP_"}
    sr = split_result(mixed_result, rules)
    app = sr.get("app")
    assert app is not None
    assert set(app.result.keys()) == {"APP_DEBUG", "APP_SECRET"}


def test_unmatched_keys_go_to_unmatched(mixed_result):
    rules = {"database": "DB_", "app": "APP_", "cloud": "AWS_"}
    sr = split_result(mixed_result, rules)
    assert set(sr.unmatched.keys()) == {"UNRELATED"}


def test_empty_rules_raises(mixed_result):
    with pytest.raises(SplitterError, match="must not be empty"):
        split_result(mixed_result, {})


def test_invalid_regex_raises(mixed_result):
    with pytest.raises(SplitterError, match="Invalid pattern"):
        split_result(mixed_result, {"bad": "[unclosed"}, use_regex=True)


def test_regex_mode_works(mixed_result):
    rules = {"db_or_app": r"^(DB|APP)_"}
    sr = split_result(mixed_result, rules, use_regex=True)
    slc = sr.get("db_or_app")
    assert slc is not None
    assert len(slc.result) == 4


def test_get_unknown_slice_returns_none(mixed_result):
    rules = {"database": "DB_"}
    sr = split_result(mixed_result, rules)
    assert sr.get("nonexistent") is None


def test_key_count_property(mixed_result):
    rules = {"database": "DB_"}
    sr = split_result(mixed_result, rules)
    db = sr.get("database")
    assert db is not None
    assert db.key_count == 2


def test_all_keys_matched_leaves_empty_unmatched():
    result: DiffResult = {"X_FOO": ("a", "b"), "X_BAR": ("c", "c")}
    rules = {"x": "X_"}
    sr = split_result(result, rules)
    assert sr.unmatched == {}
