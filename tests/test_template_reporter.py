"""Tests for envoy_diff.template_reporter."""
from __future__ import annotations

import json
import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.templater import generate_template, TemplateResult
from envoy_diff.template_reporter import (
    format_template_text,
    format_template_json,
    format_template_markdown,
    render_template,
)


@pytest.fixture()
def empty_tmpl() -> TemplateResult:
    result = DiffResult(
        missing_in_target={},
        missing_in_source={},
        mismatched={},
        matching={},
    )
    return generate_template(result)


@pytest.fixture()
def full_tmpl() -> TemplateResult:
    result = DiffResult(
        missing_in_target={"DB_URL": "postgres://localhost/db"},
        missing_in_source={},
        mismatched={"SECRET_KEY": ("abc", "xyz")},
        matching={},
    )
    return generate_template(result)


def test_text_empty_result(empty_tmpl: TemplateResult) -> None:
    text = format_template_text(empty_tmpl)
    assert "no keys" in text


def test_text_shows_key_count(full_tmpl: TemplateResult) -> None:
    text = format_template_text(full_tmpl)
    assert "2" in text


def test_text_shows_key_names(full_tmpl: TemplateResult) -> None:
    text = format_template_text(full_tmpl)
    assert "DB_URL" in text
    assert "SECRET_KEY" in text


def test_text_shows_comments(full_tmpl: TemplateResult) -> None:
    text = format_template_text(full_tmpl)
    assert "missing" in text
    assert "mismatch" in text


def test_json_is_valid(full_tmpl: TemplateResult) -> None:
    raw = format_template_json(full_tmpl)
    data = json.loads(raw)
    assert data["key_count"] == 2
    assert isinstance(data["entries"], list)


def test_json_entry_fields(full_tmpl: TemplateResult) -> None:
    data = json.loads(format_template_json(full_tmpl))
    entry = next(e for e in data["entries"] if e["key"] == "DB_URL")
    assert entry["placeholder"] == "postgres://localhost/db"
    assert entry["comment"] == "missing"


def test_json_empty_result(empty_tmpl: TemplateResult) -> None:
    data = json.loads(format_template_json(empty_tmpl))
    assert data["key_count"] == 0
    assert data["entries"] == []


def test_markdown_contains_table(full_tmpl: TemplateResult) -> None:
    md = format_template_markdown(full_tmpl)
    assert "|" in md
    assert "DB_URL" in md


def test_markdown_empty_result(empty_tmpl: TemplateResult) -> None:
    md = format_template_markdown(empty_tmpl)
    assert "No keys" in md


def test_render_defaults_to_text(full_tmpl: TemplateResult) -> None:
    out = render_template(full_tmpl)
    assert "=== .env Template ==" in out


def test_render_json(full_tmpl: TemplateResult) -> None:
    out = render_template(full_tmpl, fmt="json")
    assert json.loads(out)["key_count"] == 2


def test_render_markdown(full_tmpl: TemplateResult) -> None:
    out = render_template(full_tmpl, fmt="markdown")
    assert "##" in out
