"""Tests for envoy_diff.summarizer and envoy_diff.summary_reporter."""

import json
import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.summarizer import SummaryStats, summarize
from envoy_diff.summary_reporter import (
    format_summary_text,
    format_summary_json,
    format_summary_markdown,
    render_summary,
)


@pytest.fixture()
def clean_result() -> DiffResult:
    return DiffResult(
        missing_in_target=[],
        missing_in_source=[],
        mismatched={},
        matching={"A": "1", "B": "2"},
    )


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        missing_in_target=["X"],
        missing_in_source=["Y", "Z"],
        mismatched={"W": ("old", "new")},
        matching={"A": "1"},
    )


# --- summarize() ---

def test_summarize_clean_result(clean_result):
    stats = summarize(clean_result)
    assert stats.total_keys == 2
    assert stats.matching == 2
    assert stats.missing_in_target == 0
    assert stats.missing_in_source == 0
    assert stats.mismatched == 0


def test_summarize_diff_result(diff_result):
    stats = summarize(diff_result)
    assert stats.total_keys == 5
    assert stats.missing_in_target == 1
    assert stats.missing_in_source == 2
    assert stats.mismatched == 1
    assert stats.matching == 1


def test_drift_ratio_zero_for_clean(clean_result):
    stats = summarize(clean_result)
    assert stats.drift_ratio == 0.0


def test_drift_percent_non_zero_for_diff(diff_result):
    stats = summarize(diff_result)
    assert stats.drift_percent > 0


def test_headline_in_sync(clean_result):
    stats = summarize(clean_result)
    assert "in sync" in stats.headline()


def test_headline_shows_drift(diff_result):
    stats = summarize(diff_result)
    headline = stats.headline()
    assert "drift" in headline
    assert "missing in target" in headline


def test_empty_result_headline():
    empty = DiffResult(missing_in_target=[], missing_in_source=[], mismatched={}, matching={})
    stats = summarize(empty)
    assert "No keys" in stats.headline()


# --- reporters ---

def test_text_contains_total(diff_result):
    stats = summarize(diff_result)
    text = format_summary_text(stats)
    assert "Total keys" in text
    assert str(stats.total_keys) in text


def test_json_is_valid(diff_result):
    stats = summarize(diff_result)
    data = json.loads(format_summary_json(stats))
    assert data["total_keys"] == stats.total_keys
    assert "drift_percent" in data


def test_markdown_has_table(diff_result):
    stats = summarize(diff_result)
    md = format_summary_markdown(stats)
    assert "|" in md
    assert "Drift" in md


def test_render_summary_dispatches_json(diff_result):
    stats = summarize(diff_result)
    out = render_summary(stats, fmt="json")
    assert out.startswith("{")


def test_render_summary_dispatches_markdown(diff_result):
    stats = summarize(diff_result)
    out = render_summary(stats, fmt="markdown")
    assert out.startswith("##")


def test_render_summary_default_is_text(clean_result):
    stats = summarize(clean_result)
    out = render_summary(stats)
    assert "===" in out
