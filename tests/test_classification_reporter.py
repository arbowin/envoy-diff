"""Tests for envoy_diff.classification_reporter."""
from __future__ import annotations

import json

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.classifier import classify_result, KeyCategory
from envoy_diff.classification_reporter import (
    format_classification_text,
    format_classification_json,
    format_classification_markdown,
    render_classification,
)


@pytest.fixture()
def classified():
    dr = DiffResult(
        source_path=".env.prod",
        target_path=".env.staging",
        missing_in_target=["DB_PASSWORD"],
        missing_in_source=["FEATURE_BETA"],
        mismatched={"LOG_LEVEL": ("error", "debug")},
        matching={"APP_PORT": "8080"},
    )
    return classify_result(dr)


def test_text_contains_source_and_target(classified):
    out = format_classification_text(classified)
    assert ".env.prod" in out
    assert ".env.staging" in out


def test_text_shows_category_header(classified):
    out = format_classification_text(classified)
    assert "AUTH" in out or "DATABASE" in out


def test_text_lists_key(classified):
    out = format_classification_text(classified)
    assert "DB_PASSWORD" in out


def test_json_is_valid(classified):
    out = format_classification_json(classified)
    parsed = json.loads(out)
    assert "categories" in parsed
    assert parsed["source_path"] == ".env.prod"


def test_json_contains_auth_category(classified):
    out = format_classification_json(classified)
    parsed = json.loads(out)
    assert KeyCategory.AUTH.value in parsed["categories"]


def test_markdown_has_heading(classified):
    out = format_classification_markdown(classified)
    assert out.startswith("## Classification Report")


def test_markdown_contains_key(classified):
    out = format_classification_markdown(classified)
    assert "DB_PASSWORD" in out


def test_render_text_default(classified):
    out = render_classification(classified)
    assert "Classification Report" in out


def test_render_json_format(classified):
    out = render_classification(classified, fmt="json")
    json.loads(out)  # must not raise


def test_render_markdown_format(classified):
    out = render_classification(classified, fmt="markdown")
    assert "##" in out
