"""Tests for envoy_diff.linter."""
from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from envoy_diff.linter import LintSeverity, lint_env_file


def write_env(tmp_path: Path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return str(p)


def test_clean_file_passes(tmp_path):
    path = write_env(tmp_path, """
        APP_NAME=myapp
        DEBUG=false
        PORT=8080
    """)
    result = lint_env_file(path)
    assert result.passed
    assert result.issues == []


def test_missing_equals_is_error(tmp_path):
    path = write_env(tmp_path, "BROKEN_LINE\n")
    result = lint_env_file(path)
    errors = result.errors
    assert len(errors) == 1
    assert "no '='" in errors[0].message


def test_duplicate_key_is_warning(tmp_path):
    path = write_env(tmp_path, "KEY=first\nKEY=second\n")
    result = lint_env_file(path)
    warnings = result.warnings
    assert any("Duplicate" in w.message for w in warnings)


def test_lowercase_key_is_info(tmp_path):
    path = write_env(tmp_path, "my_key=value\n")
    result = lint_env_file(path)
    info = [i for i in result.issues if i.severity == LintSeverity.INFO]
    assert any("uppercase" in i.message for i in info)


def test_value_with_trailing_space_is_warning(tmp_path):
    path = write_env(tmp_path, "KEY=value   \n")
    result = lint_env_file(path)
    warnings = result.warnings
    assert any("whitespace" in w.message for w in warnings)


def test_comments_and_blank_lines_are_skipped(tmp_path):
    path = write_env(tmp_path, """
        # this is a comment

        APP=ok
    """)
    result = lint_env_file(path)
    assert result.passed
    assert result.issues == []


def test_empty_key_is_error(tmp_path):
    path = write_env(tmp_path, "=value\n")
    result = lint_env_file(path)
    assert any(i.severity == LintSeverity.ERROR and "Empty key" in i.message for i in result.issues)


def test_lint_issue_str_includes_severity_and_line(tmp_path):
    path = write_env(tmp_path, "bad_key=val\n")
    result = lint_env_file(path)
    issue_str = str(result.issues[0])
    assert "INFO" in issue_str
    assert "line 1" in issue_str


def test_passed_false_when_errors_present(tmp_path):
    path = write_env(tmp_path, "NO_EQUALS\n")
    result = lint_env_file(path)
    assert not result.passed
