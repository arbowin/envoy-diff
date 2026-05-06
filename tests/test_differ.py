"""Tests for envoy_diff.differ module."""

import pytest
from pathlib import Path

from envoy_diff.differ import diff_files, DiffOptions, DiffError
from envoy_diff.filter import FilterOptions
from envoy_diff.sorter import SortKey


@pytest.fixture()
def source_env(tmp_path: Path) -> Path:
    p = tmp_path / "source.env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n")
    return p


@pytest.fixture()
def target_env(tmp_path: Path) -> Path:
    p = tmp_path / "target.env"
    p.write_text("DB_HOST=prod.example.com\nDB_PORT=5432\nNEW_VAR=hello\n")
    return p


def test_diff_files_returns_report(source_env, target_env):
    report = diff_files(source_env, target_env)
    assert report.result is not None
    assert report.source_path == str(source_env)
    assert report.target_path == str(target_env)


def test_diff_files_detects_mismatch(source_env, target_env):
    report = diff_files(source_env, target_env)
    keys = {entry.key for entry in report.result.mismatched}
    assert "DB_HOST" in keys


def test_diff_files_detects_missing_in_target(source_env, target_env):
    report = diff_files(source_env, target_env)
    keys = {entry.key for entry in report.result.missing_in_target}
    assert "SECRET_KEY" in keys


def test_diff_files_detects_missing_in_source(source_env, target_env):
    report = diff_files(source_env, target_env)
    keys = {entry.key for entry in report.result.missing_in_source}
    assert "NEW_VAR" in keys


def test_diff_files_includes_validation_by_default(source_env, target_env):
    report = diff_files(source_env, target_env)
    assert report.source_validation is not None
    assert report.target_validation is not None


def test_diff_files_skips_validation_when_disabled(source_env, target_env):
    options = DiffOptions(validate=False)
    report = diff_files(source_env, target_env, options=options)
    assert report.source_validation is None
    assert report.target_validation is None


def test_diff_files_applies_filter(source_env, target_env):
    options = DiffOptions(filter=FilterOptions(pattern="DB_*"))
    report = diff_files(source_env, target_env, options=options)
    all_keys = (
        {e.key for e in report.result.mismatched}
        | {e.key for e in report.result.missing_in_target}
        | {e.key for e in report.result.missing_in_source}
        | {e.key for e in report.result.matching}
    )
    assert all(k.startswith("DB_") for k in all_keys)


def test_diff_files_raises_on_missing_source(tmp_path, target_env):
    with pytest.raises(DiffError, match="source"):
        diff_files(tmp_path / "nonexistent.env", target_env)


def test_diff_files_raises_on_missing_target(source_env, tmp_path):
    with pytest.raises(DiffError, match="target"):
        diff_files(source_env, tmp_path / "nonexistent.env")


def test_diff_files_sort_by_key(source_env, target_env):
    options = DiffOptions(sort_by=SortKey.KEY, sort_descending=False)
    report = diff_files(source_env, target_env, options=options)
    assert report.result is not None
