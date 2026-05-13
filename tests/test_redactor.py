"""Tests for envoy_diff.redactor."""

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.redactor import (
    RedactError,
    RedactOptions,
    REDACTED_PLACEHOLDER,
    redact_result,
)


@pytest.fixture()
def mixed_result() -> DiffResult:
    return DiffResult(
        diffs={
            "APP_NAME": ("myapp", "myapp"),
            "DB_PASSWORD": ("hunter2", "s3cr3t"),
            "API_TOKEN": ("tok_abc", None),
            "SECRET_KEY": (None, "newkey"),
            "PORT": ("8080", "9090"),
        }
    )


def test_non_sensitive_keys_are_unchanged(mixed_result):
    out = redact_result(mixed_result)
    assert out.diffs["APP_NAME"] == ("myapp", "myapp")
    assert out.diffs["PORT"] == ("8080", "9090")


def test_password_key_is_redacted(mixed_result):
    out = redact_result(mixed_result)
    src, tgt = out.diffs["DB_PASSWORD"]
    assert src == REDACTED_PLACEHOLDER
    assert tgt == REDACTED_PLACEHOLDER


def test_token_key_with_none_target_is_redacted(mixed_result):
    out = redact_result(mixed_result)
    src, tgt = out.diffs["API_TOKEN"]
    assert src == REDACTED_PLACEHOLDER
    # target was None — absence is preserved
    assert tgt is None


def test_secret_key_with_none_source_is_redacted(mixed_result):
    out = redact_result(mixed_result)
    src, tgt = out.diffs["SECRET_KEY"]
    assert src is None
    assert tgt == REDACTED_PLACEHOLDER


def test_custom_placeholder(mixed_result):
    opts = RedactOptions(placeholder="<hidden>")
    out = redact_result(mixed_result, opts)
    assert out.diffs["DB_PASSWORD"] == ("<hidden>", "<hidden>")


def test_custom_pattern_redacts_matching_key():
    result = DiffResult(diffs={"STRIPE_LIVE_KEY": ("sk_live_abc", "sk_live_xyz")})
    opts = RedactOptions(patterns=[r"stripe"])
    out = redact_result(result, opts)
    assert out.diffs["STRIPE_LIVE_KEY"] == (REDACTED_PLACEHOLDER, REDACTED_PLACEHOLDER)


def test_custom_pattern_does_not_redact_unmatched_key():
    result = DiffResult(diffs={"APP_NAME": ("foo", "bar")})
    opts = RedactOptions(patterns=[r"stripe"])
    out = redact_result(result, opts)
    assert out.diffs["APP_NAME"] == ("foo", "bar")


def test_invalid_pattern_raises_redact_error():
    result = DiffResult(diffs={"KEY": ("a", "b")})
    opts = RedactOptions(patterns=[r"["])
    with pytest.raises(RedactError, match="Invalid redact pattern"):
        redact_result(result, opts)


def test_redact_does_not_mutate_original(mixed_result):
    original_diffs = dict(mixed_result.diffs)
    redact_result(mixed_result)
    assert mixed_result.diffs == original_diffs


def test_empty_result_returns_empty_result():
    result = DiffResult(diffs={})
    out = redact_result(result)
    assert out.diffs == {}
