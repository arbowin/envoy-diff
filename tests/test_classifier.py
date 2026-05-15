"""Tests for envoy_diff.classifier."""
from __future__ import annotations

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.classifier import KeyCategory, classify_result


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        source_path=".env.source",
        target_path=".env.target",
        missing_in_target=["DB_HOST", "JWT_SECRET"],
        missing_in_source=["S3_BUCKET"],
        mismatched={"LOG_LEVEL": ("debug", "info"), "APP_PORT": ("8000", "9000")},
        matching={"FEATURE_DARK_MODE": "true", "REDIS_URL": "redis://localhost"},
    )


def test_classify_returns_classified_result(diff_result):
    cr = classify_result(diff_result)
    assert cr.source_path == ".env.source"
    assert cr.target_path == ".env.target"


def test_database_keys_classified(diff_result):
    cr = classify_result(diff_result)
    db_keys = cr.keys_in(KeyCategory.DATABASE)
    assert "DB_HOST" in db_keys
    assert "REDIS_URL" in db_keys


def test_auth_keys_classified(diff_result):
    cr = classify_result(diff_result)
    auth_keys = cr.keys_in(KeyCategory.AUTH)
    assert "JWT_SECRET" in auth_keys


def test_storage_keys_classified(diff_result):
    cr = classify_result(diff_result)
    storage_keys = cr.keys_in(KeyCategory.STORAGE)
    assert "S3_BUCKET" in storage_keys


def test_logging_keys_classified(diff_result):
    cr = classify_result(diff_result)
    log_keys = cr.keys_in(KeyCategory.LOGGING)
    assert "LOG_LEVEL" in log_keys


def test_feature_flag_keys_classified(diff_result):
    cr = classify_result(diff_result)
    ff_keys = cr.keys_in(KeyCategory.FEATURE_FLAG)
    assert "FEATURE_DARK_MODE" in ff_keys


def test_other_keys_classified(diff_result):
    cr = classify_result(diff_result)
    other_keys = cr.keys_in(KeyCategory.OTHER)
    assert "APP_PORT" in other_keys


def test_all_categories_only_returns_non_empty(diff_result):
    cr = classify_result(diff_result)
    active = cr.all_categories()
    for cat in active:
        assert cr.keys_in(cat), f"{cat} should be non-empty"


def test_keys_within_category_are_sorted(diff_result):
    cr = classify_result(diff_result)
    for cat in KeyCategory:
        keys = cr.keys_in(cat)
        assert keys == sorted(keys)


def test_empty_diff_produces_no_categories():
    empty = DiffResult(
        source_path="a",
        target_path="b",
        missing_in_target=[],
        missing_in_source=[],
        mismatched={},
        matching={},
    )
    cr = classify_result(empty)
    assert cr.all_categories() == []
