"""Tests for envoy_diff.profiler."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from envoy_diff.profiler import ProfileError, ProfileResult, profile_env_file


def write_env(content: str) -> Path:
    fd, name = tempfile.mkstemp(suffix=".env")
    with os.fdopen(fd, "w") as fh:
        fh.write(content)
    return Path(name)


# ---------------------------------------------------------------------------
# Basic stats
# ---------------------------------------------------------------------------

def test_profile_total_keys():
    p = write_env("A=1\nB=2\nC=3\n")
    result = profile_env_file(p)
    assert result.total_keys == 3


def test_profile_empty_values():
    p = write_env("A=\nB=hello\nC=\n")
    result = profile_env_file(p)
    assert result.empty_values == 2
    assert result.non_empty_values == 1


def test_profile_empty_ratio():
    p = write_env("A=\nB=x\n")
    result = profile_env_file(p)
    assert result.empty_ratio == pytest.approx(0.5)


def test_profile_empty_ratio_no_keys():
    p = write_env("# comment only\n")
    result = profile_env_file(p)
    assert result.empty_ratio == 0.0


# ---------------------------------------------------------------------------
# Longest key / value
# ---------------------------------------------------------------------------

def test_profile_longest_key():
    p = write_env("SHORT=1\nVERY_LONG_KEY_NAME=2\n")
    result = profile_env_file(p)
    assert result.longest_key == "VERY_LONG_KEY_NAME"


def test_profile_longest_value_key():
    p = write_env("A=hi\nB=a_much_longer_value_here\n")
    result = profile_env_file(p)
    assert result.longest_value_key == "B"


# ---------------------------------------------------------------------------
# Prefixes
# ---------------------------------------------------------------------------

def test_profile_unique_prefixes():
    p = write_env("DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=myapp\nNOUNDERSCORE=1\n")
    result = profile_env_file(p)
    assert "DB" in result.unique_prefixes
    assert "APP" in result.unique_prefixes
    assert "NOUNDERSCORE" not in result.unique_prefixes


# ---------------------------------------------------------------------------
# Path & errors
# ---------------------------------------------------------------------------

def test_profile_records_path():
    p = write_env("X=1\n")
    result = profile_env_file(p)
    assert result.path == str(p)


def test_profile_missing_file_raises():
    with pytest.raises(ProfileError):
        profile_env_file("/nonexistent/path/.env")


def test_profile_result_is_profile_result_instance():
    p = write_env("A=1\n")
    result = profile_env_file(p)
    assert isinstance(result, ProfileResult)
