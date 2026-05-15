"""Tests for envoy_diff.split_reporter."""

from __future__ import annotations

import json

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.splitter import split_result, SplitResult
from envoy_diff.split_reporter import (
    format_split_text,
    format_split_json,
    format_split_markdown,
    render_split,
)


@pytest.fixture()
def split() -> SplitResult:
    result: DiffResult = {
        "DB_HOST": ("localhost", "prod-db"),
        "APP_DEBUG": ("true", None),
        "MISC": ("x", "y"),
    }
    return split_result(result, {"database": "DB_", "app": "APP_"})


def test_text_contains_slice_names(split):
    out = format_split_text(split)
    assert "[database]" in out
    assert "[app]" in out


def test_text_contains_unmatched_section(split):
    out = format_split_text(split)
    assert "[unmatched]" in out


def test_text_shows_key_count(split):
    out = format_split_text(split)
    assert "1 keys" in out


def test_json_is_valid(split):
    out = format_split_json(split)
    data = json.loads(out)
    assert "slices" in data
    assert "unmatched" in data


def test_json_slice_names(split):
    data = json.loads(format_split_json(split))
    names = [s["name"] for s in data["slices"]]
    assert "database" in names
    assert "app" in names


def test_json_unmatched_keys(split):
    data = json.loads(format_split_json(split))
    assert "MISC" in data["unmatched"]


def test_markdown_contains_headers(split):
    out = format_split_markdown(split)
    assert "### database" in out
    assert "### app" in out


def test_render_text(split):
    assert render_split(split, "text") == format_split_text(split)


def test_render_json(split):
    assert render_split(split, "json") == format_split_json(split)


def test_render_markdown(split):
    assert render_split(split, "markdown") == format_split_markdown(split)


def test_render_md_alias(split):
    assert render_split(split, "md") == format_split_markdown(split)


def test_empty_slice_shows_no_keys_message():
    result: DiffResult = {"APP_X": ("a", "b")}
    sr = split_result(result, {"database": "DB_", "app": "APP_"})
    out = format_split_text(sr)
    assert "(no keys)" in out
