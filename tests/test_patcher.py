"""Tests for envoy_diff.patcher."""

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.patcher import (
    PatchEntry,
    PatchResult,
    generate_patch,
    patch_to_lines,
)


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"NEW_KEY": "new_value"},
        missing_in_source={"OLD_KEY": "old_value"},
        mismatched={"CHANGED": ("src_val", "tgt_val")},
        common={"SAME": ("v", "v")},
    )


def test_generate_patch_adds_missing_in_target(diff_result):
    patch = generate_patch(diff_result)
    adds = patch.by_action("add")
    assert len(adds) == 1
    assert adds[0].key == "NEW_KEY"
    assert adds[0].source_value == "new_value"
    assert adds[0].target_value is None


def test_generate_patch_excludes_removals_by_default(diff_result):
    patch = generate_patch(diff_result)
    assert patch.by_action("remove") == []


def test_generate_patch_includes_removals_when_requested(diff_result):
    patch = generate_patch(diff_result, include_removals=True)
    removes = patch.by_action("remove")
    assert len(removes) == 1
    assert removes[0].key == "OLD_KEY"
    assert removes[0].target_value == "old_value"


def test_generate_patch_updates_mismatched(diff_result):
    patch = generate_patch(diff_result)
    updates = patch.by_action("update")
    assert len(updates) == 1
    assert updates[0].key == "CHANGED"
    assert updates[0].source_value == "src_val"
    assert updates[0].target_value == "tgt_val"


def test_generate_patch_entries_sorted_by_key():
    result = DiffResult(
        missing_in_target={"ZEBRA": "z", "ALPHA": "a"},
        missing_in_source={},
        mismatched={},
        common={},
    )
    patch = generate_patch(result)
    keys = [e.key for e in patch.entries]
    assert keys == sorted(keys)


def test_patch_is_empty_when_no_differences():
    result = DiffResult(
        missing_in_target={},
        missing_in_source={},
        mismatched={},
        common={"K": ("v", "v")},
    )
    patch = generate_patch(result)
    assert patch.is_empty


def test_patch_entry_as_line_add():
    entry = PatchEntry(key="FOO", action="add", source_value="bar", target_value=None)
    assert entry.as_line() == "FOO=bar"


def test_patch_entry_as_line_update():
    entry = PatchEntry(key="FOO", action="update", source_value="new", target_value="old")
    assert entry.as_line() == "FOO=new"


def test_patch_entry_as_line_remove():
    entry = PatchEntry(key="OLD", action="remove", source_value=None, target_value="v")
    assert entry.as_line() == "# REMOVE: OLD"


def test_patch_entry_as_line_none_value():
    entry = PatchEntry(key="EMPTY", action="add", source_value=None, target_value=None)
    assert entry.as_line() == "EMPTY="


def test_patch_to_lines_returns_list(diff_result):
    patch = generate_patch(diff_result)
    lines = patch_to_lines(patch)
    assert isinstance(lines, list)
    assert all(isinstance(ln, str) for ln in lines)
    assert len(lines) == len(patch.entries)
