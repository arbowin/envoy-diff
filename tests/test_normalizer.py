"""Tests for envoy_diff.normalizer."""

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.normalizer import NormalizeOptions, normalize_result


@pytest.fixture()
def whitespace_result() -> DiffResult:
    return DiffResult(
        differences={
            "KEY_A": ("hello ", "hello"),
            "KEY_B": (" world", "world"),
            "KEY_C": ("different", "values"),
        }
    )


@pytest.fixture()
def bool_result() -> DiffResult:
    return DiffResult(
        differences={
            "FLAG_1": ("True", "true"),
            "FLAG_2": ("YES", "1"),
            "FLAG_3": ("False", "0"),
            "FLAG_4": ("on", "off"),
        }
    )


def test_default_strips_whitespace_and_removes_cosmetic_mismatch(whitespace_result):
    result = normalize_result(whitespace_result)
    assert "KEY_A" not in result.differences
    assert "KEY_B" not in result.differences


def test_default_keeps_real_differences(whitespace_result):
    result = normalize_result(whitespace_result)
    assert "KEY_C" in result.differences


def test_normalize_booleans_collapses_aliases(bool_result):
    opts = NormalizeOptions(normalize_booleans=True)
    result = normalize_result(bool_result, opts)
    # FLAG_1: 'True' -> 'true', 'true' -> 'true'  => equal, removed
    assert "FLAG_1" not in result.differences
    # FLAG_2: 'YES' -> 'true', '1' -> 'true'       => equal, removed
    assert "FLAG_2" not in result.differences
    # FLAG_3: 'False' -> 'false', '0' -> 'false'   => equal, removed
    assert "FLAG_3" not in result.differences
    # FLAG_4: 'on' -> 'true', 'off' -> 'false'     => different, kept
    assert "FLAG_4" in result.differences


def test_normalize_empty_to_none_makes_equal():
    result = DiffResult(differences={"EMPTY": ("", None)})
    opts = NormalizeOptions(normalize_empty_to_none=True)
    out = normalize_result(result, opts)
    assert "EMPTY" not in out.differences


def test_normalize_empty_to_none_keeps_real_diff():
    result = DiffResult(differences={"KEY": ("", "something")})
    opts = NormalizeOptions(normalize_empty_to_none=True)
    out = normalize_result(result, opts)
    assert "KEY" in out.differences


def test_lowercase_values_removes_case_only_mismatch():
    result = DiffResult(differences={"HOST": ("Localhost", "localhost")})
    opts = NormalizeOptions(lowercase_values=True)
    out = normalize_result(result, opts)
    assert "HOST" not in out.differences


def test_none_source_or_target_preserved():
    result = DiffResult(
        differences={
            "MISSING_TGT": ("value", None),
            "MISSING_SRC": (None, "value"),
        }
    )
    out = normalize_result(result)
    assert "MISSING_TGT" in out.differences
    assert "MISSING_SRC" in out.differences


def test_normalize_does_not_mutate_original(whitespace_result):
    original_keys = set(whitespace_result.differences.keys())
    normalize_result(whitespace_result)
    assert set(whitespace_result.differences.keys()) == original_keys


def test_empty_result_returns_empty_result():
    result = DiffResult(differences={})
    out = normalize_result(result)
    assert out.differences == {}
