"""Tests for envoy_diff.writer."""

import pytest
from pathlib import Path

from envoy_diff.comparator import DiffResult
from envoy_diff.exporter import ExportFormat
from envoy_diff.writer import WriterError, export_to_string, write_export


@pytest.fixture()
def simple_result() -> DiffResult:
    return DiffResult(
        source={"KEY": "val"},
        target={},
        missing_in_target={"KEY"},
        missing_in_source=set(),
        mismatched={},
    )


def test_export_to_string_csv(simple_result):
    out = export_to_string(simple_result, ExportFormat.CSV)
    assert "KEY" in out
    assert "missing_in_target" in out


def test_export_to_string_html(simple_result):
    out = export_to_string(simple_result, ExportFormat.HTML)
    assert "<table" in out
    assert "KEY" in out


def test_export_to_string_bad_format_raises(simple_result):
    with pytest.raises(WriterError):
        export_to_string(simple_result, "toml")  # type: ignore[arg-type]


def test_write_export_creates_csv_file(tmp_path, simple_result):
    dest = tmp_path / "report.csv"
    write_export(simple_result, ExportFormat.CSV, output_path=dest)
    assert dest.exists()
    content = dest.read_text()
    assert "KEY" in content


def test_write_export_creates_html_file(tmp_path, simple_result):
    dest = tmp_path / "subdir" / "report.html"
    write_export(simple_result, ExportFormat.HTML, output_path=dest)
    assert dest.exists()
    assert "<html>" in dest.read_text()


def test_write_export_creates_parent_dirs(tmp_path, simple_result):
    dest = tmp_path / "a" / "b" / "c" / "out.csv"
    write_export(simple_result, ExportFormat.CSV, output_path=dest)
    assert dest.exists()


def test_write_export_stdout_does_not_raise(simple_result, capsys):
    write_export(simple_result, ExportFormat.CSV, output_path=None)
    captured = capsys.readouterr()
    assert "KEY" in captured.out


def test_write_export_bad_format_raises_writer_error(tmp_path, simple_result):
    dest = tmp_path / "out.xml"
    with pytest.raises(WriterError):
        write_export(simple_result, "xml", output_path=dest)  # type: ignore[arg-type]
