"""Tests for envoy_diff.merger."""

from __future__ import annotations

from pathlib import Path

import pytest

from envoy_diff.merger import MergeError, MergeResult, merge_env_files


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_merge_empty_list_returns_empty_result():
    result = merge_env_files([])
    assert isinstance(result, MergeResult)
    assert result.merged == {}
    assert result.key_count == 0


def test_merge_single_file(tmp_path):
    p = write_env(tmp_path, "a.env", "FOO=bar\nBAZ=qux\n")
    result = merge_env_files([p])
    assert result.merged == {"FOO": "bar", "BAZ": "qux"}
    assert result.overridden == []


def test_later_file_overrides_earlier(tmp_path):
    base = write_env(tmp_path, "base.env", "FOO=base\nSHARED=old\n")
    override = write_env(tmp_path, "override.env", "SHARED=new\nEXTRA=yes\n")
    result = merge_env_files([base, override])
    assert result.merged["SHARED"] == "new"
    assert result.merged["FOO"] == "base"
    assert result.merged["EXTRA"] == "yes"


def test_overridden_keys_recorded(tmp_path):
    a = write_env(tmp_path, "a.env", "KEY=first\n")
    b = write_env(tmp_path, "b.env", "KEY=second\n")
    result = merge_env_files([a, b])
    assert "KEY" in result.overridden


def test_source_tracks_winning_file(tmp_path):
    a = write_env(tmp_path, "a.env", "KEY=first\n")
    b = write_env(tmp_path, "b.env", "KEY=second\n")
    result = merge_env_files([a, b])
    assert result.sources["KEY"] == b


def test_merge_three_files_last_wins(tmp_path):
    a = write_env(tmp_path, "a.env", "X=1\n")
    b = write_env(tmp_path, "b.env", "X=2\n")
    c = write_env(tmp_path, "c.env", "X=3\n")
    result = merge_env_files([a, b, c])
    assert result.merged["X"] == "3"
    assert result.sources["X"] == c


def test_merge_missing_file_raises(tmp_path):
    missing = tmp_path / "ghost.env"
    with pytest.raises(MergeError, match="ghost.env"):
        merge_env_files([missing])


def test_key_count_property(tmp_path):
    p = write_env(tmp_path, "a.env", "A=1\nB=2\nC=3\n")
    result = merge_env_files([p])
    assert result.key_count == 3
