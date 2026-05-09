"""Tests for envoy_diff.annotator and envoy_diff.annotation_reporter."""

import json
import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.annotator import annotate_result, Annotation, AnnotatedResult
from envoy_diff.annotation_reporter import (
    format_annotation_text,
    format_annotation_json,
    format_annotation_markdown,
    render_annotation,
)


@pytest.fixture()
def clean_result() -> DiffResult:
    return DiffResult(
        missing_in_target=set(),
        missing_in_source=set(),
        mismatched={},
        common={"KEY": "val"},
    )


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"ALPHA"},
        missing_in_source={"BETA"},
        mismatched={"GAMMA": ("old", "new")},
        common={},
    )


def test_annotate_clean_result_has_no_annotations(clean_result):
    ar = annotate_result(clean_result)
    assert not ar.has_annotations
    assert ar.annotations == []


def test_annotate_diff_result_produces_annotations(diff_result):
    ar = annotate_result(diff_result)
    assert ar.has_annotations
    assert len(ar.annotations) == 3


def test_annotation_statuses_are_correct(diff_result):
    ar = annotate_result(diff_result)
    statuses = {a.status for a in ar.annotations}
    assert statuses == {"missing_in_target", "missing_in_source", "mismatch"}


def test_by_status_filters_correctly(diff_result):
    ar = annotate_result(diff_result)
    missing = ar.by_status("missing_in_target")
    assert len(missing) == 1
    assert missing[0].key == "ALPHA"


def test_annotation_str_contains_key_and_status(diff_result):
    ar = annotate_result(diff_result)
    ann = ar.by_status("mismatch")[0]
    text = str(ann)
    assert "GAMMA" in text
    assert "mismatch" in text


def test_text_format_clean(clean_result):
    ar = annotate_result(clean_result)
    out = format_annotation_text(ar)
    assert "in sync" in out


def test_text_format_diff(diff_result):
    ar = annotate_result(diff_result)
    out = format_annotation_text(ar)
    assert "ALPHA" in out
    assert "BETA" in out
    assert "GAMMA" in out


def test_json_format_is_valid_json(diff_result):
    ar = annotate_result(diff_result)
    out = format_annotation_json(ar)
    data = json.loads(out)
    assert isinstance(data, list)
    assert len(data) == 3
    keys = {item["key"] for item in data}
    assert keys == {"ALPHA", "BETA", "GAMMA"}


def test_markdown_format_clean(clean_result):
    ar = annotate_result(clean_result)
    out = format_annotation_markdown(ar)
    assert "in sync" in out


def test_markdown_format_diff_has_table(diff_result):
    ar = annotate_result(diff_result)
    out = format_annotation_markdown(ar)
    assert "|" in out
    assert "GAMMA" in out


def test_render_annotation_unknown_format_raises(diff_result):
    ar = annotate_result(diff_result)
    with pytest.raises(ValueError, match="Unknown annotation format"):
        render_annotation(ar, fmt="xml")


def test_render_annotation_markdown_alias(diff_result):
    ar = annotate_result(diff_result)
    assert render_annotation(ar, fmt="md") == render_annotation(ar, fmt="markdown")
