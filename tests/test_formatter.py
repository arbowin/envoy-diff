"""Tests for envoy_diff.formatter module."""

import json

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.formatter import OutputFormat, format_result


@pytest.fixture
def empty_result() -> DiffResult:
    return DiffResult(missing_in_target=set(), missing_in_source=set(), mismatched_values={})


@pytest.fixture
def full_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"DB_HOST", "SECRET_KEY"},
        missing_in_source={"NEW_FEATURE_FLAG"},
        mismatched_values={"LOG_LEVEL": ("DEBUG", "INFO"), "PORT": ("8000", "9000")},
    )


# --- TEXT format ---

def test_text_no_differences(empty_result):
    output = format_result(empty_result, OutputFormat.TEXT)
    assert "No differences found." in output


def test_text_missing_in_target(full_result):
    output = format_result(full_result, OutputFormat.TEXT, source_name="dev", target_name="prod")
    assert "Missing in prod:" in output
    assert "DB_HOST" in output
    assert "SECRET_KEY" in output


def test_text_missing_in_source(full_result):
    output = format_result(full_result, OutputFormat.TEXT, source_name="dev", target_name="prod")
    assert "Missing in dev:" in output
    assert "NEW_FEATURE_FLAG" in output


def test_text_mismatched_values(full_result):
    output = format_result(full_result, OutputFormat.TEXT)
    assert "Mismatched values:" in output
    assert "LOG_LEVEL" in output
    assert "'DEBUG'" in output
    assert "'INFO'" in output


# --- JSON format ---

def test_json_no_differences(empty_result):
    output = format_result(empty_result, OutputFormat.JSON, source_name="a", target_name="b")
    data = json.loads(output)
    assert data["missing_in_b"] == []
    assert data["missing_in_a"] == []
    assert data["mismatched_values"] == {}


def test_json_full_result(full_result):
    output = format_result(full_result, OutputFormat.JSON, source_name="dev", target_name="prod")
    data = json.loads(output)
    assert "DB_HOST" in data["missing_in_prod"]
    assert "NEW_FEATURE_FLAG" in data["missing_in_dev"]
    assert "LOG_LEVEL" in data["mismatched_values"]
    assert data["mismatched_values"]["LOG_LEVEL"]["dev"] == "DEBUG"
    assert data["mismatched_values"]["LOG_LEVEL"]["prod"] == "INFO"


# --- MARKDOWN format ---

def test_markdown_no_differences(empty_result):
    output = format_result(empty_result, OutputFormat.MARKDOWN)
    assert "No differences found." in output
    assert output.startswith("# Env Diff Report")


def test_markdown_contains_headers(full_result):
    output = format_result(full_result, OutputFormat.MARKDOWN, source_name="dev", target_name="prod")
    assert "## Missing in `prod`" in output
    assert "## Missing in `dev`" in output
    assert "## Mismatched Values" in output


def test_markdown_table_contains_keys(full_result):
    output = format_result(full_result, OutputFormat.MARKDOWN)
    assert "`LOG_LEVEL`" in output
    assert "`PORT`" in output


def test_output_format_values():
    assert OutputFormat.TEXT == "text"
    assert OutputFormat.JSON == "json"
    assert OutputFormat.MARKDOWN == "markdown"
