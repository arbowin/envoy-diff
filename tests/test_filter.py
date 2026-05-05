"""Tests for envoy_diff.filter module."""

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.filter import FilterOptions, filter_result


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"DB_HOST": "localhost", "API_KEY": "secret"},
        missing_in_source={"CACHE_URL": "redis://localhost"},
        mismatched={"LOG_LEVEL": ("debug", "info"), "DB_PORT": ("5432", "3306")},
    )


def test_no_filter_returns_all(sample_result):
    opts = FilterOptions()
    filtered = filter_result(sample_result, opts)
    assert filtered.missing_in_target == sample_result.missing_in_target
    assert filtered.missing_in_source == sample_result.missing_in_source
    assert filtered.mismatched == sample_result.mismatched


def test_glob_pattern_filters_keys(sample_result):
    opts = FilterOptions(pattern="DB_*")
    filtered = filter_result(sample_result, opts)
    assert "DB_HOST" in filtered.missing_in_target
    assert "API_KEY" not in filtered.missing_in_target
    assert "DB_PORT" in filtered.mismatched
    assert "LOG_LEVEL" not in filtered.mismatched


def test_regex_pattern_filters_keys(sample_result):
    opts = FilterOptions(pattern=r"^(DB|LOG)", use_regex=True)
    filtered = filter_result(sample_result, opts)
    assert "DB_HOST" in filtered.missing_in_target
    assert "API_KEY" not in filtered.missing_in_target
    assert "LOG_LEVEL" in filtered.mismatched
    assert "CACHE_URL" not in filtered.missing_in_source


def test_exclude_missing_in_target(sample_result):
    opts = FilterOptions(include_missing_in_target=False)
    filtered = filter_result(sample_result, opts)
    assert filtered.missing_in_target == {}
    assert filtered.missing_in_source == sample_result.missing_in_source
    assert filtered.mismatched == sample_result.mismatched


def test_exclude_missing_in_source(sample_result):
    opts = FilterOptions(include_missing_in_source=False)
    filtered = filter_result(sample_result, opts)
    assert filtered.missing_in_source == {}


def test_exclude_mismatched(sample_result):
    opts = FilterOptions(include_mismatched=False)
    filtered = filter_result(sample_result, opts)
    assert filtered.mismatched == {}


def test_pattern_with_no_matches_returns_empty(sample_result):
    opts = FilterOptions(pattern="NONEXISTENT_*")
    filtered = filter_result(sample_result, opts)
    assert filtered.missing_in_target == {}
    assert filtered.missing_in_source == {}
    assert filtered.mismatched == {}


def test_filter_empty_result():
    empty = DiffResult()
    opts = FilterOptions(pattern="DB_*")
    filtered = filter_result(empty, opts)
    assert filtered.missing_in_target == {}
    assert filtered.missing_in_source == {}
    assert filtered.mismatched == {}
