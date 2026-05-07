"""Tests for envoy_diff.auditor and envoy_diff.audit_reporter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envoy_diff.auditor import (
    AuditError,
    AuditLog,
    load_audit_log,
    record_audit,
    save_audit_log,
)
from envoy_diff.audit_reporter import (
    format_audit_json,
    format_audit_markdown,
    format_audit_text,
    render_audit,
)
from envoy_diff.comparator import DiffResult


@pytest.fixture()
def clean_result() -> DiffResult:
    return DiffResult(missing_in_target=set(), missing_in_source=set(), mismatched=set())


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"DB_HOST"},
        missing_in_source={"NEW_KEY"},
        mismatched={"API_URL"},
    )


def test_record_audit_creates_entry(clean_result):
    entry = record_audit("a.env", "b.env", clean_result, note="ci run")
    assert entry.source_path == "a.env"
    assert entry.target_path == "b.env"
    assert entry.note == "ci run"
    assert "T" in entry.timestamp  # ISO format


def test_audit_log_add_and_len(clean_result):
    log = AuditLog()
    assert len(log) == 0
    log.add(record_audit("a.env", "b.env", clean_result))
    assert len(log) == 1


def test_save_and_load_round_trip(tmp_path, diff_result):
    log = AuditLog()
    log.add(record_audit("src.env", "tgt.env", diff_result, note="test"))
    out = str(tmp_path / "audit.json")
    save_audit_log(log, out)
    loaded = load_audit_log(out)
    assert len(loaded) == 1
    e = loaded.entries[0]
    assert e.source_path == "src.env"
    assert e.result.missing_in_target == {"DB_HOST"}
    assert e.note == "test"


def test_load_missing_file_raises():
    with pytest.raises(AuditError, match="Failed to read"):
        load_audit_log("/nonexistent/audit.json")


def test_save_bad_path_raises(clean_result):
    log = AuditLog()
    log.add(record_audit("a.env", "b.env", clean_result))
    with pytest.raises(AuditError, match="Failed to write"):
        save_audit_log(log, "/nonexistent/dir/audit.json")


def test_format_text_clean(clean_result):
    log = AuditLog()
    log.add(record_audit("a.env", "b.env", clean_result))
    text = format_audit_text(log)
    assert "CLEAN" in text
    assert "a.env" in text


def test_format_text_diff(diff_result):
    log = AuditLog()
    log.add(record_audit("a.env", "b.env", diff_result))
    text = format_audit_text(log)
    assert "DIFF" in text
    assert "DB_HOST" in text
    assert "API_URL" in text


def test_format_text_empty_log():
    assert "No audit" in format_audit_text(AuditLog())


def test_format_json(diff_result):
    log = AuditLog()
    log.add(record_audit("s.env", "t.env", diff_result))
    data = json.loads(format_audit_json(log))
    assert data[0]["status"] == "DIFF"
    assert "DB_HOST" in data[0]["missing_in_target"]


def test_format_markdown(diff_result):
    log = AuditLog()
    log.add(record_audit("s.env", "t.env", diff_result))
    md = format_audit_markdown(log)
    assert "| Timestamp" in md
    assert "DIFF" in md


def test_render_audit_dispatches(clean_result):
    log = AuditLog()
    log.add(record_audit("a.env", "b.env", clean_result))
    assert "CLEAN" in render_audit(log, "text")
    assert "status" in render_audit(log, "json")
    assert "---" in render_audit(log, "markdown")
