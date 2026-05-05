"""Tests for envoy_diff.reporter."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.formatter import OutputFormat
from envoy_diff.reporter import ReportError, report_to_string, write_report


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(missing_in_target=[], missing_in_source=[], mismatched={})


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        missing_in_target=["DB_HOST"],
        missing_in_source=["NEW_KEY"],
        mismatched={"LOG_LEVEL": ("debug", "info")},
    )


def test_report_to_string_text(diff_result: DiffResult) -> None:
    output = report_to_string(diff_result, OutputFormat.TEXT)
    assert "DB_HOST" in output
    assert "LOG_LEVEL" in output


def test_report_to_string_json(diff_result: DiffResult) -> None:
    output = report_to_string(diff_result, OutputFormat.JSON)
    assert "missing_in_target" in output
    assert "DB_HOST" in output


def test_report_to_string_markdown(diff_result: DiffResult) -> None:
    output = report_to_string(diff_result, OutputFormat.MARKDOWN)
    assert "#" in output
    assert "DB_HOST" in output


def test_write_report_to_stream(diff_result: DiffResult) -> None:
    buf = io.StringIO()
    write_report(diff_result, OutputFormat.TEXT, stream=buf)
    buf.seek(0)
    content = buf.read()
    assert "DB_HOST" in content


def test_write_report_defaults_to_stdout(diff_result: DiffResult, capsys) -> None:
    write_report(diff_result)
    captured = capsys.readouterr()
    assert "DB_HOST" in captured.out


def test_write_report_to_file(diff_result: DiffResult, tmp_path: Path) -> None:
    out_file = tmp_path / "report.txt"
    write_report(diff_result, OutputFormat.TEXT, output_path=out_file)
    assert out_file.exists()
    assert "DB_HOST" in out_file.read_text()


def test_write_report_creates_parent_dirs(diff_result: DiffResult, tmp_path: Path) -> None:
    out_file = tmp_path / "nested" / "dir" / "report.md"
    write_report(diff_result, OutputFormat.MARKDOWN, output_path=out_file)
    assert out_file.exists()


def test_write_report_file_error(diff_result: DiffResult) -> None:
    bad_path = Path("/no_permission_root_dir/report.txt")
    with pytest.raises(ReportError, match="Failed to write report"):
        write_report(diff_result, output_path=bad_path)


def test_write_report_empty_result_no_newline_duplication(empty_result: DiffResult) -> None:
    buf = io.StringIO()
    write_report(empty_result, OutputFormat.TEXT, stream=buf)
    buf.seek(0)
    content = buf.read()
    assert not content.endswith("\n\n")
