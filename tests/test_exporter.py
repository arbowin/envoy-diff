"""Tests for envoy_diff.exporter."""

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.exporter import ExportError, ExportFormat, export_csv, export_html, export_result


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(
        source={"A": "1"},
        target={"A": "1"},
        missing_in_target=set(),
        missing_in_source=set(),
        mismatched={},
    )


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        source={"FOO": "bar", "ONLY_SRC": "x", "MISMATCH": "old"},
        target={"FOO": "bar", "ONLY_TGT": "y", "MISMATCH": "new"},
        missing_in_target={"ONLY_SRC"},
        missing_in_source={"ONLY_TGT"},
        mismatched={"MISMATCH": ("old", "new")},
    )


# --- CSV ---

def test_csv_no_differences_has_header_only(empty_result):
    output = export_csv(empty_result)
    lines = [l for l in output.strip().splitlines() if l]
    assert len(lines) == 1
    assert lines[0] == "key,status,source_value,target_value"


def test_csv_contains_missing_in_target(diff_result):
    output = export_csv(diff_result)
    assert "ONLY_SRC" in output
    assert "missing_in_target" in output


def test_csv_contains_missing_in_source(diff_result):
    output = export_csv(diff_result)
    assert "ONLY_TGT" in output
    assert "missing_in_source" in output


def test_csv_contains_mismatched(diff_result):
    output = export_csv(diff_result)
    assert "MISMATCH" in output
    assert "mismatched" in output
    assert "old" in output
    assert "new" in output


# --- HTML ---

def test_html_contains_doctype(diff_result):
    output = export_html(diff_result)
    assert output.startswith("<!DOCTYPE html>")


def test_html_no_differences_shows_message(empty_result):
    output = export_html(empty_result)
    assert "No differences found." in output


def test_html_contains_all_keys(diff_result):
    output = export_html(diff_result)
    for key in ("ONLY_SRC", "ONLY_TGT", "MISMATCH"):
        assert key in output


def test_html_custom_title():
    result = DiffResult(
        source={}, target={},
        missing_in_target=set(), missing_in_source=set(), mismatched={},
    )
    output = export_html(result, title="My Custom Title")
    assert "My Custom Title" in output


# --- dispatch ---

def test_export_result_csv(diff_result):
    output = export_result(diff_result, ExportFormat.CSV)
    assert "key,status" in output


def test_export_result_html(diff_result):
    output = export_result(diff_result, ExportFormat.HTML)
    assert "<table" in output


def test_export_result_unknown_raises():
    result = DiffResult(
        source={}, target={},
        missing_in_target=set(), missing_in_source=set(), mismatched={},
    )
    with pytest.raises(ExportError):
        export_result(result, "xml")  # type: ignore[arg-type]
