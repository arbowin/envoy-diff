"""Tests for envoy_diff.tagger."""

from __future__ import annotations

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.tagger import TagRule, TaggedResult, tag_result


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        missing_in_target=["DB_PASSWORD", "AWS_SECRET"],
        missing_in_source=["LEGACY_TOKEN"],
        mismatched={"APP_ENV": ("production", "staging"), "DB_HOST": ("prod-db", "dev-db")},
    )


@pytest.fixture()
def rules() -> list[TagRule]:
    return [
        TagRule(pattern="DB_*", tag="database"),
        TagRule(pattern="AWS_*", tag="cloud"),
        TagRule(pattern="*TOKEN*", tag="secret"),
        TagRule(pattern="*PASSWORD*", tag="secret"),
        TagRule(pattern="APP_*", tag="app"),
    ]


def test_tag_result_returns_tagged_result(diff_result, rules):
    result = tag_result(diff_result, rules)
    assert isinstance(result, TaggedResult)


def test_all_keys_are_present(diff_result, rules):
    result = tag_result(diff_result, rules)
    keys = {e.key for e in result.entries}
    assert "DB_PASSWORD" in keys
    assert "AWS_SECRET" in keys
    assert "LEGACY_TOKEN" in keys
    assert "APP_ENV" in keys
    assert "DB_HOST" in keys


def test_db_keys_tagged_database(diff_result, rules):
    result = tag_result(diff_result, rules)
    db_entries = {e.key: e for e in result.entries}
    assert "database" in db_entries["DB_PASSWORD"].tags
    assert "database" in db_entries["DB_HOST"].tags


def test_aws_key_tagged_cloud(diff_result, rules):
    result = tag_result(diff_result, rules)
    entry = next(e for e in result.entries if e.key == "AWS_SECRET")
    assert "cloud" in entry.tags


def test_password_key_tagged_secret(diff_result, rules):
    result = tag_result(diff_result, rules)
    entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert "secret" in entry.tags


def test_unmatched_key_has_no_tags(diff_result):
    result = tag_result(diff_result, [])
    for entry in result.entries:
        assert entry.tags == []


def test_all_tags_returns_sorted_unique(diff_result, rules):
    result = tag_result(diff_result, rules)
    tags = result.all_tags()
    assert tags == sorted(set(tags))
    assert "database" in tags
    assert "secret" in tags


def test_by_tag_filters_correctly(diff_result, rules):
    result = tag_result(diff_result, rules)
    db_entries = result.by_tag("database")
    assert all("database" in e.tags for e in db_entries)


def test_len_equals_total_keys(diff_result, rules):
    result = tag_result(diff_result, rules)
    assert len(result) == 5


def test_empty_diff_produces_empty_result():
    empty = DiffResult(missing_in_target=[], missing_in_source=[], mismatched={})
    result = tag_result(empty, [TagRule(pattern="*", tag="all")])
    assert len(result) == 0
    assert result.all_tags() == []
