"""Tests for envoy_diff.comparator module."""

import pytest
from envoy_diff.comparator import compare_envs, DiffResult


def test_compare_identical_envs():
    source = {"HOST": "localhost", "PORT": "8080", "DEBUG": "true"}
    target = {"HOST": "localhost", "PORT": "8080", "DEBUG": "true"}
    result = compare_envs(source, target)
    assert not result.has_differences
    assert result.matching == source


def test_compare_missing_in_target():
    source = {"HOST": "localhost", "PORT": "8080", "SECRET": "abc"}
    target = {"HOST": "localhost", "PORT": "8080"}
    result = compare_envs(source, target)
    assert result.has_differences
    assert "SECRET" in result.missing_in_target
    assert result.missing_in_target["SECRET"] == "abc"
    assert not result.missing_in_source


def test_compare_missing_in_source():
    source = {"HOST": "localhost"}
    target = {"HOST": "localhost", "EXTRA_KEY": "value"}
    result = compare_envs(source, target)
    assert result.has_differences
    assert "EXTRA_KEY" in result.missing_in_source
    assert not result.missing_in_target


def test_compare_mismatched_values():
    source = {"HOST": "localhost", "PORT": "8080"}
    target = {"HOST": "production.example.com", "PORT": "8080"}
    result = compare_envs(source, target)
    assert result.has_differences
    assert "HOST" in result.mismatched
    assert result.mismatched["HOST"] == ("localhost", "production.example.com")
    assert "PORT" in result.matching


def test_compare_none_values():
    source = {"EMPTY_KEY": None, "SET_KEY": "value"}
    target = {"EMPTY_KEY": None, "SET_KEY": "value"}
    result = compare_envs(source, target)
    assert not result.has_differences


def test_compare_none_vs_value_mismatch():
    source = {"KEY": None}
    target = {"KEY": "some_value"}
    result = compare_envs(source, target)
    assert "KEY" in result.mismatched
    assert result.mismatched["KEY"] == (None, "some_value")


def test_compare_empty_envs():
    result = compare_envs({}, {})
    assert not result.has_differences


def test_summary_no_differences():
    result = DiffResult(matching={"KEY": "val"})
    assert result.summary() == "No differences found."


def test_summary_with_differences():
    source = {"A": "1", "B": "old", "C": "only_source"}
    target = {"A": "1", "B": "new", "D": "only_target"}
    result = compare_envs(source, target)
    summary = result.summary()
    assert "Missing in target" in summary
    assert "C" in summary
    assert "Missing in source" in summary
    assert "D" in summary
    assert "Mismatched values" in summary
    assert "B" in summary
