"""Tests for envoy_diff.tag_reporter."""

from __future__ import annotations

import json

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.tagger import TagRule, TaggedResult, tag_result
from envoy_diff.tag_reporter import (
    format_tag_json,
    format_tag_markdown,
    format_tag_text,
    render_tag,
)


@pytest.fixture()
def empty_tagged() -> TaggedResult:
    diff = DiffResult(missing_in_target=[], missing_in_source=[], mismatched={})
    return tag_result(diff, [])


@pytest.fixture()
def full_tagged() -> TaggedResult:
    diff = DiffResult(
        missing_in_target=["DB_PASSWORD"],
        missing_in_source=["LEGACY_TOKEN"],
        mismatched={"APP_ENV": ("prod", "staging")},
    )
    rules = [
        TagRule(pattern="DB_*", tag="database"),
        TagRule(pattern="*TOKEN*", tag="secret"),
        TagRule(pattern="APP_*", tag="app"),
    ]
    return tag_result(diff, rules)


def test_text_empty_result(empty_tagged):
    output = format_tag_text(empty_tagged)
    assert "No tagged entries" in output


def test_text_shows_tags_present(full_tagged):
    output = format_tag_text(full_tagged)
    assert "app" in output
    assert "database" in output
    assert "secret" in output


def test_text_shows_key_names(full_tagged):
    output = format_tag_text(full_tagged)
    assert "DB_PASSWORD" in output
    assert "APP_ENV" in output


def test_json_is_valid(full_tagged):
    output = format_tag_json(full_tagged)
    data = json.loads(output)
    assert "tags" in data
    assert "entries" in data


def test_json_entries_have_expected_keys(full_tagged):
    data = json.loads(format_tag_json(full_tagged))
    for entry in data["entries"]:
        assert "key" in entry
        assert "tags" in entry


def test_json_empty_result(empty_tagged):
    data = json.loads(format_tag_json(empty_tagged))
    assert data["entries"] == []
    assert data["tags"] == []


def test_markdown_contains_header(full_tagged):
    output = format_tag_markdown(full_tagged)
    assert "## Tagged Diff Entries" in output


def test_markdown_contains_table_row(full_tagged):
    output = format_tag_markdown(full_tagged)
    assert "|" in output
    assert "DB_PASSWORD" in output


def test_markdown_empty_result(empty_tagged):
    output = format_tag_markdown(empty_tagged)
    assert "No tagged entries" in output


def test_render_tag_text(full_tagged):
    assert render_tag(full_tagged, "text") == format_tag_text(full_tagged)


def test_render_tag_json(full_tagged):
    assert render_tag(full_tagged, "json") == format_tag_json(full_tagged)


def test_render_tag_markdown(full_tagged):
    assert render_tag(full_tagged, "markdown") == format_tag_markdown(full_tagged)
