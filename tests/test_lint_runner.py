"""Tests for envoy_diff.lint_runner."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envoy_diff.lint_runner import LintRunError, LintSeverity, run_lint


def write_env(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return str(p)


def test_run_lint_single_clean_file(tmp_path):
    path = write_env(tmp_path, "a.env", "APP=ok\nDEBUG=false\n")
    report = run_lint([path])
    assert report.all_passed
    assert report.total_errors == 0


def test_run_lint_multiple_files(tmp_path):
    p1 = write_env(tmp_path, "a.env", "APP=ok\n")
    p2 = write_env(tmp_path, "b.env", "NO_EQUALS\n")
    report = run_lint([p1, p2])
    assert not report.all_passed
    assert report.total_errors == 1
    assert report.results[p1].passed
    assert not report.results[p2].passed


def test_run_lint_missing_file_raises(tmp_path):
    with pytest.raises(LintRunError, match="Cannot read"):
        run_lint(["/nonexistent/path/.env"])


def test_min_severity_filters_info(tmp_path):
    path = write_env(tmp_path, "a.env", "lower_key=val\n")
    report_all = run_lint([path])
    report_warn = run_lint([path], min_severity=LintSeverity.WARNING)
    # INFO issue for lowercase key should be absent at WARNING threshold
    info_in_all = [i for i in report_all.results[path].issues if i.severity == LintSeverity.INFO]
    assert len(info_in_all) > 0
    assert report_warn.results[path].issues == []


def test_summary_contains_pass_fail(tmp_path):
    p1 = write_env(tmp_path, "good.env", "KEY=val\n")
    p2 = write_env(tmp_path, "bad.env", "BROKEN\n")
    report = run_lint([p1, p2])
    summary = report.summary()
    assert "PASS" in summary
    assert "FAIL" in summary


def test_total_warnings_aggregated(tmp_path):
    p1 = write_env(tmp_path, "a.env", "KEY=val  \n")
    p2 = write_env(tmp_path, "b.env", "OTHER=val  \n")
    report = run_lint([p1, p2])
    assert report.total_warnings >= 2


def test_empty_paths_returns_empty_report():
    report = run_lint([])
    assert report.all_passed
    assert report.results == {}
    assert report.summary() == ""
