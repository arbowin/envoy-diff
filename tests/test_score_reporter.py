"""Tests for envoy_diff.score_reporter."""

import json

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.scorer import score_diff
from envoy_diff.score_reporter import (
    format_score_json,
    format_score_markdown,
    format_score_text,
    render_score,
)


@pytest.fixture()
def perfect_sr():
    result = DiffResult(
        missing_in_target=[],
        missing_in_source=[],
        mismatched={},
        common={"A": "1"},
    )
    return score_diff(result)


@pytest.fixture()
def diff_sr():
    result = DiffResult(
        missing_in_target=["X"],
        missing_in_source=["Y"],
        mismatched={"Z": ("a", "b")},
        common={},
    )
    return score_diff(result)


def test_text_contains_score(perfect_sr):
    text = format_score_text(perfect_sr)
    assert "100/100" in text


def test_text_perfect_sync_message(perfect_sr):
    text = format_score_text(perfect_sr)
    assert "perfect sync" in text.lower()


def test_text_no_perfect_message_for_diff(diff_sr):
    text = format_score_text(diff_sr)
    assert "perfect sync" not in text.lower()


def test_json_is_valid(diff_sr):
    raw = format_score_json(diff_sr)
    data = json.loads(raw)
    assert "score" in data
    assert "grade" in data


def test_json_fields_match_result(diff_sr):
    data = json.loads(format_score_json(diff_sr))
    assert data["missing_in_target"] == diff_sr.missing_in_target
    assert data["missing_in_source"] == diff_sr.missing_in_source
    assert data["mismatched"] == diff_sr.mismatched


def test_markdown_contains_table(diff_sr):
    md = format_score_markdown(diff_sr)
    assert "|" in md
    assert "Score" in md


def test_markdown_perfect_note(perfect_sr):
    md = format_score_markdown(perfect_sr)
    assert "perfect sync" in md.lower()


def test_render_score_text(diff_sr):
    out = render_score(diff_sr, fmt="text")
    assert "Health Score" in out


def test_render_score_json(diff_sr):
    out = render_score(diff_sr, fmt="json")
    json.loads(out)  # must not raise


def test_render_score_markdown(diff_sr):
    out = render_score(diff_sr, fmt="markdown")
    assert "##" in out


def test_render_score_md_alias(diff_sr):
    assert render_score(diff_sr, fmt="md") == render_score(diff_sr, fmt="markdown")


def test_render_score_bad_format_raises(diff_sr):
    with pytest.raises(ValueError, match="Unknown format"):
        render_score(diff_sr, fmt="xml")
