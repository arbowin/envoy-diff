"""Tests for envoy_diff.baseline_reporter."""

import json

import pytest

from envoy_diff.baseline import BaselineComparison
from envoy_diff.baseline_reporter import (
    format_baseline_json,
    format_baseline_markdown,
    format_baseline_text,
    render_baseline,
)


@pytest.fixture()
def clean_cmp() -> BaselineComparison:
    return BaselineComparison(new_keys=[], resolved_keys=[], unchanged_keys=[])


@pytest.fixture()
def diff_cmp() -> BaselineComparison:
    return BaselineComparison(
        new_keys=["NEW_KEY"],
        resolved_keys=["OLD_KEY"],
        unchanged_keys=["SAME_KEY"],
    )


def test_text_no_changes(clean_cmp: BaselineComparison) -> None:
    out = format_baseline_text(clean_cmp)
    assert "No changes" in out


def test_text_shows_new_keys(diff_cmp: BaselineComparison) -> None:
    out = format_baseline_text(diff_cmp)
    assert "NEW_KEY" in out
    assert "New issues" in out


def test_text_shows_resolved_keys(diff_cmp: BaselineComparison) -> None:
    out = format_baseline_text(diff_cmp)
    assert "OLD_KEY" in out
    assert "Resolved" in out


def test_json_is_valid(diff_cmp: BaselineComparison) -> None:
    data = json.loads(format_baseline_json(diff_cmp))
    assert data["new_keys"] == ["NEW_KEY"]
    assert data["resolved_keys"] == ["OLD_KEY"]
    assert data["has_regressions"] is True
    assert data["has_improvements"] is True


def test_json_clean(clean_cmp: BaselineComparison) -> None:
    data = json.loads(format_baseline_json(clean_cmp))
    assert data["has_regressions"] is False


def test_markdown_contains_headings(diff_cmp: BaselineComparison) -> None:
    out = format_baseline_markdown(diff_cmp)
    assert "## Baseline" in out
    assert "### New Issues" in out
    assert "`NEW_KEY`" in out


def test_markdown_no_changes(clean_cmp: BaselineComparison) -> None:
    out = format_baseline_markdown(clean_cmp)
    assert "_No changes" in out


def test_render_delegates_text(diff_cmp: BaselineComparison) -> None:
    assert render_baseline(diff_cmp, fmt="text") == format_baseline_text(diff_cmp)


def test_render_delegates_json(diff_cmp: BaselineComparison) -> None:
    assert render_baseline(diff_cmp, fmt="json") == format_baseline_json(diff_cmp)


def test_render_delegates_markdown(diff_cmp: BaselineComparison) -> None:
    assert render_baseline(diff_cmp, fmt="md") == format_baseline_markdown(diff_cmp)
