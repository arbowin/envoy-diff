"""Tests for envoy_diff.watchdog_reporter."""

from __future__ import annotations

import json
import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.differ import DiffReport, DiffOptions
from envoy_diff.watchdog import WatchEvent
from envoy_diff.watchdog_reporter import (
    format_watch_text,
    format_watch_json,
    format_watch_markdown,
    render_watch,
)


def _make_event(missing_in_target=None, mismatched=None) -> WatchEvent:
    result = DiffResult(
        missing_in_target=set(missing_in_target or []),
        missing_in_source=set(),
        mismatched=mismatched or {},
    )
    report = DiffReport(
        source="source.env",
        target="target.env",
        result=result,
        options=DiffOptions(),
    )
    return WatchEvent(
        path="target.env",
        previous_mtime=1000.0,
        current_mtime=2000.0,
        report=report,
    )


@pytest.fixture
def clean_event():
    return _make_event()


@pytest.fixture
def diff_event():
    return _make_event(
        missing_in_target=["DB_HOST"],
        mismatched={"APP_ENV": ("production", "staging")},
    )


def test_text_contains_timestamp(clean_event):
    out = format_watch_text(clean_event)
    assert "Change detected" in out


def test_text_contains_path(clean_event):
    out = format_watch_text(clean_event)
    assert "target.env" in out


def test_text_shows_missing_key(diff_event):
    out = format_watch_text(diff_event)
    assert "DB_HOST" in out


def test_json_is_valid(diff_event):
    out = format_watch_json(diff_event)
    data = json.loads(out)
    assert "timestamp" in data
    assert "missing_in_target" in data
    assert "DB_HOST" in data["missing_in_target"]


def test_json_mismatched_structure(diff_event):
    data = json.loads(format_watch_json(diff_event))
    assert "APP_ENV" in data["mismatched"]
    assert data["mismatched"]["APP_ENV"]["source"] == "production"


def test_markdown_contains_heading(diff_event):
    out = format_watch_markdown(diff_event)
    assert out.startswith("## Change detected")


def test_render_watch_defaults_to_text(clean_event):
    assert render_watch(clean_event) == format_watch_text(clean_event)


def test_render_watch_json(diff_event):
    out = render_watch(diff_event, fmt="json")
    assert json.loads(out)["has_differences"] is True


def test_render_watch_markdown(diff_event):
    out = render_watch(diff_event, fmt="markdown")
    assert "##" in out
