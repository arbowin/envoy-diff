"""Tests for envoy_diff.grouper."""

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.grouper import GroupedResult, group_result


@pytest.fixture()
def mixed_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"DB_HOST": "localhost", "APP_NAME": "myapp"},
        missing_in_source={"AWS_REGION": "us-east-1"},
        mismatched={"DB_PORT": ("5432", "3306"), "APP_ENV": ("prod", "staging")},
        matching={"DB_USER": "admin", "AWS_KEY": "abc"},
    )


def test_group_names_are_sorted(mixed_result):
    gr = group_result(mixed_result)
    assert gr.group_names == sorted(gr.group_names)


def test_db_group_contains_db_keys(mixed_result):
    gr = group_result(mixed_result)
    assert "DB" in gr.groups
    db = gr.groups["DB"]
    assert "DB_HOST" in db.missing_in_target
    assert "DB_PORT" in db.mismatched
    assert "DB_USER" in db.matching


def test_app_group_contains_app_keys(mixed_result):
    gr = group_result(mixed_result)
    assert "APP" in gr.groups
    app = gr.groups["APP"]
    assert "APP_NAME" in app.missing_in_target
    assert "APP_ENV" in app.mismatched


def test_aws_group_contains_aws_keys(mixed_result):
    gr = group_result(mixed_result)
    assert "AWS" in gr.groups
    aws = gr.groups["AWS"]
    assert "AWS_REGION" in aws.missing_in_source
    assert "AWS_KEY" in aws.matching


def test_empty_result_yields_empty_groups():
    result = DiffResult(
        missing_in_target={},
        missing_in_source={},
        mismatched={},
        matching={},
    )
    gr = group_result(result)
    assert gr.groups == {}


def test_key_without_separator_uses_full_name():
    result = DiffResult(
        missing_in_target={"NOPREFIX": "val"},
        missing_in_source={},
        mismatched={},
        matching={},
    )
    gr = group_result(result)
    assert "NOPREFIX" in gr.groups


def test_get_returns_none_for_unknown_group(mixed_result):
    gr = group_result(mixed_result)
    assert gr.get("UNKNOWN") is None


def test_custom_separator():
    result = DiffResult(
        missing_in_target={"DB.HOST": "localhost"},
        missing_in_source={},
        mismatched={},
        matching={},
    )
    gr = group_result(result, separator=".")
    assert "DB" in gr.groups
