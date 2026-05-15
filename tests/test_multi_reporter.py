"""Tests for envoy_diff.multi_reporter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envoy_diff.differ_multi import diff_multi
from envoy_diff.multi_reporter import (
    format_multi_text,
    format_multi_json,
    format_multi_markdown,
    render_multi,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def source(tmp_path: Path) -> Path:
    p = tmp_path / "source.env"
    p.write_text("APP=foo\nSECRET=xyz\nDEBUG=true\n")
    return p


@pytest.fixture()
def staging(tmp_path: Path) -> Path:
    p = tmp_path / "staging.env"
    p.write_text("APP=foo\nDEBUG=false\n")
    return p


@pytest.fixture()
def prod(tmp_path: Path) -> Path:
    p = tmp_path / "prod.env"
    p.write_text("APP=foo\nSECRET=xyz\nDEBUG=true\n")
    return p


@pytest.fixture()
def multi_report(source, staging, prod):
    return diff_multi(source, {"staging": staging, "prod": prod})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_text_contains_source_path(multi_report, source):
    text = format_multi_text(multi_report)
    assert str(source) in text


def test_text_contains_target_labels(multi_report):
    text = format_multi_text(multi_report)
    assert "staging" in text
    assert "prod" in text


def test_json_is_valid(multi_report):
    raw = format_multi_json(multi_report)
    data = json.loads(raw)
    assert "source" in data
    assert "targets" in data
    assert "staging" in data["targets"]
    assert "prod" in data["targets"]


def test_markdown_has_heading(multi_report):
    md = format_multi_markdown(multi_report)
    assert "# Multi-diff Report" in md


def test_markdown_contains_labels(multi_report):
    md = format_multi_markdown(multi_report)
    assert "## staging" in md
    assert "## prod" in md


def test_render_text(multi_report):
    out = render_multi(multi_report, fmt="text")
    assert "staging" in out


def test_render_json(multi_report):
    out = render_multi(multi_report, fmt="json")
    data = json.loads(out)
    assert "targets" in data


def test_render_markdown(multi_report):
    out = render_multi(multi_report, fmt="markdown")
    assert "#" in out


def test_render_md_alias(multi_report):
    out = render_multi(multi_report, fmt="md")
    assert "Multi-diff" in out
