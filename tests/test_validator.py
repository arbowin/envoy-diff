"""Tests for envoy_diff.validator."""

import pytest

from envoy_diff.validator import (
    ValidationResult,
    ValidationWarning,
    validate_env,
)


def test_valid_env_returns_no_warnings():
    env = {"APP_ENV": "production", "PORT": "8080", "DEBUG": None}
    result = validate_env(env)
    assert result.is_valid
    assert result.warnings == []


def test_key_with_hyphen_is_flagged():
    result = validate_env({"MY-KEY": "value"})
    assert not result.is_valid
    assert any("MY-KEY" in w.message for w in result.warnings)


def test_key_with_space_is_flagged():
    result = validate_env({"MY KEY": "value"})
    assert not result.is_valid
    assert any("MY KEY" in w.message for w in result.warnings)


def test_key_starting_with_digit_is_flagged():
    result = validate_env({"1_KEY": "value"})
    warnings = [w for w in result.warnings if "starts with a digit" in w.message]
    assert len(warnings) == 1


def test_value_with_shell_special_chars_is_flagged():
    result = validate_env({"SECRET": "$(cat /etc/passwd)"})
    assert not result.is_valid
    keys_flagged = [w.key for w in result.warnings]
    assert "SECRET" in keys_flagged


def test_value_none_does_not_trigger_suspicious_char_warning():
    result = validate_env({"EMPTY_KEY": None})
    assert result.is_valid


def test_multiple_keys_accumulate_warnings():
    env = {
        "GOOD_KEY": "safe_value",
        "bad-key": "value",
        "ANOTHER": "`rm -rf /`",
    }
    result = validate_env(env)
    assert not result.is_valid
    assert len(result.warnings) >= 2


def test_validation_result_add_method():
    result = ValidationResult()
    result.add("SOME_KEY", "Test warning message.")
    assert len(result.warnings) == 1
    assert result.warnings[0].key == "SOME_KEY"
    assert result.warnings[0].message == "Test warning message."
    assert not result.is_valid


def test_empty_env_is_valid():
    result = validate_env({})
    assert result.is_valid
