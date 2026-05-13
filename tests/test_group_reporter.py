"""Tests for envoy_diff.group_reporter."""

import json

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.grouper import group_result
from envoy_diff.group_reporter import (
    format_group_json,
    format_group_markdown,
    format_group_text,
    render_group,
)


@pytest.fixture()
def grouped():
    result = DiffResult(
        missing_in_target={"DB_HOST": "localhost"},
        missing_in_source={"AWS_REGION": "us-east-1"},
        mismatched={"APP_ENV": ("prod", "staging")},
        matching={"DB_USER": "admin"},
    )
    return group_result(result)


def test_text_contains_group_names(grouped):
    out = format_group_text(grouped)
    assert "[DB]" in out
    assert "[AWS]" in out
    assert "[APP]" in out


def test_text_shows_missing_in_target(grouped):
    out = format_group_text(grouped)
    assert "DB_HOST" in out
    assert "missing in target" in out


def test_text_shows_missing_in_source(grouped):
    out = format_group_text(grouped)
    assert "AWS_REGION" in out
    assert "missing in source" in out


def test_text_shows_mismatch(grouped):
    out = format_group_text(grouped)
    assert "APP_ENV" in out
    assert "prod" in out
    assert "staging" in out


def test_json_is_valid_json(grouped):
    out = format_group_json(grouped)
    data = json.loads(out)
    assert "DB" in data
    assert "missing_in_target" in data["DB"]


def test_json_matching_count(grouped):
    out = format_group_json(grouped)
    data = json.loads(out)
    assert data["DB"]["matching_count"] == 1


def test_markdown_has_heading(grouped):
    out = format_group_markdown(grouped)
    assert "## Grouped Diff Results" in out


def test_markdown_shows_group_sections(grouped):
    out = format_group_markdown(grouped)
    assert "### DB" in out
    assert "### AWS" in out


def test_render_group_delegates_to_text(grouped):
    assert render_group(grouped, "text") == format_group_text(grouped)


def test_render_group_delegates_to_json(grouped):
    assert render_group(grouped, "json") == format_group_json(grouped)


def test_render_group_delegates_to_markdown(grouped):
    assert render_group(grouped, "markdown") == format_group_markdown(grouped)


def test_empty_grouped_text():
    result = DiffResult(missing_in_target={}, missing_in_source={}, mismatched={}, matching={})
    gr = group_result(result)
    out = format_group_text(gr)
    assert out == "No groups found."
