"""Tests for envoy_diff.trend and envoy_diff.trend_reporter."""

import json
from pathlib import Path

import pytest

from envoy_diff.scorer import ScoreResult
from envoy_diff.trend import TrendEntry, TrendError, TrendLog, load_trend, record_trend
from envoy_diff.trend_reporter import render_trend


@pytest.fixture()
def score_a() -> ScoreResult:
    return ScoreResult(score=80.0, grade="B", missing_in_target=1, missing_in_source=0, mismatched=1, total=5)


@pytest.fixture()
def score_b() -> ScoreResult:
    return ScoreResult(score=100.0, grade="A", missing_in_target=0, missing_in_source=0, mismatched=0, total=5)


def test_record_trend_creates_file(tmp_path: Path, score_a: ScoreResult) -> None:
    p = tmp_path / "trend.json"
    record_trend(p, score_a)
    assert p.exists()


def test_record_trend_appends_entries(tmp_path: Path, score_a: ScoreResult, score_b: ScoreResult) -> None:
    p = tmp_path / "trend.json"
    record_trend(p, score_a, label="v1")
    log = record_trend(p, score_b, label="v2")
    assert len(log) == 2
    assert log.entries[0].label == "v1"
    assert log.entries[1].label == "v2"


def test_load_trend_round_trip(tmp_path: Path, score_a: ScoreResult) -> None:
    p = tmp_path / "trend.json"
    record_trend(p, score_a, label="round-trip")
    loaded = load_trend(p)
    assert len(loaded) == 1
    assert loaded.entries[0].score == score_a.score
    assert loaded.entries[0].label == "round-trip"


def test_load_trend_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(TrendError):
        load_trend(tmp_path / "nonexistent.json")


def test_load_trend_invalid_json_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("not json", encoding="utf-8")
    with pytest.raises(TrendError):
        load_trend(p)


def test_delta_none_when_single_entry(score_a: ScoreResult) -> None:
    log = TrendLog()
    log.add(TrendEntry(timestamp="t", score=80.0, grade="B", missing_in_target=1, missing_in_source=0, mismatched=1))
    assert log.delta() is None


def test_delta_computed_correctly(score_a: ScoreResult, score_b: ScoreResult) -> None:
    log = TrendLog()
    log.add(TrendEntry(timestamp="t1", score=80.0, grade="B", missing_in_target=1, missing_in_source=0, mismatched=1))
    log.add(TrendEntry(timestamp="t2", score=100.0, grade="A", missing_in_target=0, missing_in_source=0, mismatched=0))
    assert log.delta() == 20.0


def test_render_text_contains_score(tmp_path: Path, score_a: ScoreResult) -> None:
    p = tmp_path / "trend.json"
    log = record_trend(p, score_a, label="env-check")
    output = render_trend(log, fmt="text")
    assert "80.0" in output
    assert "env-check" in output


def test_render_json_is_valid(tmp_path: Path, score_a: ScoreResult, score_b: ScoreResult) -> None:
    p = tmp_path / "trend.json"
    record_trend(p, score_a)
    log = record_trend(p, score_b)
    parsed = json.loads(render_trend(log, fmt="json"))
    assert len(parsed["entries"]) == 2
    assert parsed["delta"] == 20.0


def test_render_markdown_contains_table(tmp_path: Path, score_a: ScoreResult) -> None:
    p = tmp_path / "trend.json"
    log = record_trend(p, score_a)
    md = render_trend(log, fmt="markdown")
    assert "| Timestamp" in md
    assert "80.0" in md


def test_render_empty_log_text() -> None:
    log = TrendLog()
    output = render_trend(log, fmt="text")
    assert "No entries" in output
