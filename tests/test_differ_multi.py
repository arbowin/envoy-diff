"""Tests for envoy_diff.differ_multi."""

from __future__ import annotations

from pathlib import Path

import pytest

from envoy_diff.differ_multi import MultiDiffError, MultiDiffReport, diff_multi
from envoy_diff.differ import DiffOptions


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def source_env(tmp_path: Path) -> Path:
    p = tmp_path / "source.env"
    p.write_text("APP_NAME=envoy\nDEBUG=true\nSECRET=abc\n")
    return p


@pytest.fixture()
def target_env(tmp_path: Path) -> Path:
    p = tmp_path / "target.env"
    p.write_text("APP_NAME=envoy\nDEBUG=false\n")
    return p


@pytest.fixture()
def identical_env(tmp_path: Path) -> Path:
    p = tmp_path / "identical.env"
    p.write_text("APP_NAME=envoy\nDEBUG=true\nSECRET=abc\n")
    return p


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_diff_multi_returns_report(source_env, target_env):
    report = diff_multi(source_env, {"staging": target_env})
    assert isinstance(report, MultiDiffReport)
    assert "staging" in report.targets()


def test_diff_multi_detects_mismatch(source_env, target_env):
    report = diff_multi(source_env, {"staging": target_env})
    result = report.get("staging")
    assert result is not None
    assert result.result.has_differences()


def test_diff_multi_all_clean_when_identical(source_env, identical_env):
    report = diff_multi(source_env, {"prod": identical_env})
    assert report.all_clean()


def test_diff_multi_multiple_targets(source_env, target_env, identical_env):
    report = diff_multi(
        source_env,
        {"staging": target_env, "prod": identical_env},
    )
    assert set(report.targets()) == {"staging", "prod"}
    assert not report.all_clean()  # staging differs


def test_diff_multi_results_mapping(source_env, target_env):
    report = diff_multi(source_env, {"staging": target_env})
    results = report.results()
    assert "staging" in results
    assert results["staging"].has_differences()


def test_diff_multi_empty_targets_raises(source_env):
    with pytest.raises(MultiDiffError, match="At least one target"):
        diff_multi(source_env, {})


def test_diff_multi_missing_in_target_detected(source_env, target_env):
    report = diff_multi(source_env, {"staging": target_env})
    result = report.get("staging")
    assert "SECRET" in result.result.missing_in_target


def test_diff_multi_source_stored_on_report(source_env, target_env):
    report = diff_multi(source_env, {"staging": target_env})
    assert report.source == source_env
