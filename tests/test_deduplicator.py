"""Tests for envoy_diff.deduplicator."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from envoy_diff.deduplicator import (
    DeduplicatorError,
    DeduplicationResult,
    DuplicateEntry,
    find_duplicates,
)


def write_env(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_empty_list_returns_empty_result():
    result = find_duplicates([])
    assert isinstance(result, DeduplicationResult)
    assert result.scanned_files == []
    assert result.duplicates == []
    assert not result.has_duplicates


def test_single_file_no_duplicates(tmp_path):
    f = write_env(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    result = find_duplicates([f])
    assert not result.has_duplicates
    assert result.scanned_files == [f]


def test_two_files_no_shared_keys(tmp_path):
    f1 = write_env(tmp_path, "a.env", "FOO=1\n")
    f2 = write_env(tmp_path, "b.env", "BAR=2\n")
    result = find_duplicates([f1, f2])
    assert not result.has_duplicates


def test_shared_key_detected_as_duplicate(tmp_path):
    f1 = write_env(tmp_path, "a.env", "SHARED=1\nONLY_A=x\n")
    f2 = write_env(tmp_path, "b.env", "SHARED=2\nONLY_B=y\n")
    result = find_duplicates([f1, f2])
    assert result.has_duplicates
    assert "SHARED" in result.duplicate_keys
    assert "ONLY_A" not in result.duplicate_keys


def test_duplicate_entry_contains_both_files(tmp_path):
    f1 = write_env(tmp_path, "a.env", "KEY=1\n")
    f2 = write_env(tmp_path, "b.env", "KEY=2\n")
    result = find_duplicates([f1, f2])
    entry = next(d for d in result.duplicates if d.key == "KEY")
    assert isinstance(entry, DuplicateEntry)
    assert f1 in entry.files
    assert f2 in entry.files
    assert entry.count == 2


def test_key_in_three_files_has_count_three(tmp_path):
    files = [
        write_env(tmp_path, f"env{i}.env", "MULTI=val\n") for i in range(3)
    ]
    result = find_duplicates(files)
    entry = next(d for d in result.duplicates if d.key == "MULTI")
    assert entry.count == 3


def test_missing_file_raises_deduplicator_error(tmp_path):
    with pytest.raises(DeduplicatorError, match="not found"):
        find_duplicates(["/nonexistent/path/.env"])


def test_scanned_files_preserved_in_result(tmp_path):
    f1 = write_env(tmp_path, "a.env", "A=1\n")
    f2 = write_env(tmp_path, "b.env", "B=2\n")
    result = find_duplicates([f1, f2])
    assert set(result.scanned_files) == {f1, f2}


def test_duplicates_sorted_alphabetically(tmp_path):
    f1 = write_env(tmp_path, "a.env", "ZEBRA=1\nAPPLE=1\n")
    f2 = write_env(tmp_path, "b.env", "ZEBRA=2\nAPPLE=2\n")
    result = find_duplicates([f1, f2])
    keys = result.duplicate_keys
    assert keys == sorted(keys)
