"""Tests for envoy_diff.templater."""
from __future__ import annotations

import os
import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.templater import (
    TemplateEntry,
    TemplateError,
    TemplateResult,
    generate_template,
    write_template,
)


@pytest.fixture()
def clean_result() -> DiffResult:
    return DiffResult(
        missing_in_target={},
        missing_in_source={},
        mismatched={},
        matching={"APP_NAME": "envoy"},
    )


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"DB_HOST": "localhost", "DB_PORT": "5432"},
        missing_in_source={"LEGACY_KEY": "old"},
        mismatched={"LOG_LEVEL": ("debug", "info")},
        matching={"APP_NAME": "envoy"},
    )


def test_generate_template_clean_result_is_empty(clean_result: DiffResult) -> None:
    tmpl = generate_template(clean_result)
    assert tmpl.key_count == 0
    assert tmpl.as_text() == ""


def test_generate_template_includes_missing_in_target(diff_result: DiffResult) -> None:
    tmpl = generate_template(diff_result)
    keys = [e.key for e in tmpl.entries]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_generate_template_includes_mismatched_by_default(diff_result: DiffResult) -> None:
    tmpl = generate_template(diff_result)
    keys = [e.key for e in tmpl.entries]
    assert "LOG_LEVEL" in keys


def test_generate_template_excludes_mismatched_when_flag_false(diff_result: DiffResult) -> None:
    tmpl = generate_template(diff_result, include_mismatched=False)
    keys = [e.key for e in tmpl.entries]
    assert "LOG_LEVEL" not in keys


def test_generate_template_does_not_include_missing_in_source(diff_result: DiffResult) -> None:
    tmpl = generate_template(diff_result)
    keys = [e.key for e in tmpl.entries]
    assert "LEGACY_KEY" not in keys


def test_placeholder_uses_source_value_when_present(diff_result: DiffResult) -> None:
    tmpl = generate_template(diff_result)
    entry = next(e for e in tmpl.entries if e.key == "DB_HOST")
    assert entry.placeholder == "localhost"


def test_placeholder_override_applied(diff_result: DiffResult) -> None:
    tmpl = generate_template(diff_result, placeholder_override="CHANGEME")
    assert all(e.placeholder == "CHANGEME" for e in tmpl.entries)


def test_as_text_contains_keys(diff_result: DiffResult) -> None:
    text = generate_template(diff_result).as_text()
    assert "DB_HOST=" in text
    assert "LOG_LEVEL=" in text


def test_as_text_contains_comments(diff_result: DiffResult) -> None:
    text = generate_template(diff_result).as_text()
    assert "# missing" in text
    assert "# mismatch" in text


def test_write_template_creates_file(diff_result: DiffResult, tmp_path) -> None:
    out = str(tmp_path / "out.env")
    write_template(diff_result, out)
    assert os.path.exists(out)
    content = open(out).read()
    assert "DB_HOST=" in content


def test_write_template_raises_on_bad_path(diff_result: DiffResult) -> None:
    with pytest.raises(TemplateError):
        write_template(diff_result, "/nonexistent_dir/out.env")
