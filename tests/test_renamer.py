"""Tests for envoy_diff.renamer."""
from __future__ import annotations

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.renamer import (
    RenameError,
    RenameRule,
    apply_renames,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(entries_data: list) -> DiffResult:
    """Build a minimal DiffResult from a list of (key, src, tgt) tuples."""
    from envoy_diff.comparator import DiffEntry, EntryStatus

    entries = []
    for key, src, tgt in entries_data:
        if src is None:
            status = EntryStatus.MISSING_IN_SOURCE
        elif tgt is None:
            status = EntryStatus.MISSING_IN_TARGET
        elif src != tgt:
            status = EntryStatus.MISMATCH
        else:
            status = EntryStatus.OK
        entries.append(DiffEntry(key=key, source_value=src, target_value=tgt, status=status))

    return DiffResult(
        source_path=".env.source",
        target_path=".env.target",
        entries=entries,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def diff_result():
    return _make_result([
        ("DB_HOST", "localhost", "localhost"),
        ("DATABASE_URL", None, "postgres://prod/db"),
        ("SECRET_KEY", "abc", "xyz"),
        ("APP_PORT", "8000", None),
    ])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_apply_renames_returns_rename_result(diff_result):
    rules = [RenameRule(old_key="APP_PORT", new_key="PORT")]
    result = apply_renames(diff_result, rules)
    assert result.source_path == ".env.source"
    assert result.target_path == ".env.target"


def test_matched_rule_appears_in_matches(diff_result):
    rules = [RenameRule(old_key="APP_PORT", new_key="PORT")]
    result = apply_renames(diff_result, rules)
    assert result.has_matches
    assert result.matches[0].rule.old_key == "APP_PORT"


def test_unmatched_rule_goes_to_unmatched(diff_result):
    rules = [RenameRule(old_key="NONEXISTENT_OLD", new_key="NONEXISTENT_NEW")]
    result = apply_renames(diff_result, rules)
    assert not result.has_matches
    assert len(result.unmatched_rules) == 1


def test_values_match_when_identical(diff_result):
    # DB_HOST is OK (same value on both sides)
    rules = [RenameRule(old_key="DB_HOST", new_key="DATABASE_HOST")]
    result = apply_renames(diff_result, rules)
    assert result.matches[0].values_match


def test_values_do_not_match_for_mismatch(diff_result):
    rules = [RenameRule(old_key="SECRET_KEY", new_key="APP_SECRET")]
    result = apply_renames(diff_result, rules)
    assert not result.matches[0].values_match


def test_all_values_consistent_true_for_empty_matches():
    result = apply_renames(_make_result([]), [])
    assert result.all_values_consistent


def test_invalid_rules_type_raises(diff_result):
    with pytest.raises(RenameError):
        apply_renames(diff_result, rules=None)  # type: ignore[arg-type]


def test_multiple_rules_mixed_outcomes(diff_result):
    rules = [
        RenameRule(old_key="APP_PORT", new_key="PORT"),       # matched
        RenameRule(old_key="GHOST_KEY", new_key="SPECTER"),   # unmatched
    ]
    result = apply_renames(diff_result, rules)
    assert len(result.matches) == 1
    assert len(result.unmatched_rules) == 1
