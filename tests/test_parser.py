"""Tests for the .env file parser module."""

import os
import tempfile
import pytest

from envoy_diff.parser import parse_env_file, EnvParseError


def write_temp_env(content: str) -> str:
    """Write content to a temporary file and return its path."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False)
    tmp.write(content)
    tmp.close()
    return tmp.name


def test_parse_basic_key_value():
    path = write_temp_env("APP_NAME=envoy\nDEBUG=true\n")
    try:
        result = parse_env_file(path)
        assert result == {"APP_NAME": "envoy", "DEBUG": "true"}
    finally:
        os.unlink(path)


def test_parse_skips_comments_and_blank_lines():
    path = write_temp_env("# This is a comment\n\nKEY=value\n")
    try:
        result = parse_env_file(path)
        assert result == {"KEY": "value"}
    finally:
        os.unlink(path)


def test_parse_value_without_content_returns_none():
    path = write_temp_env("EMPTY_KEY=\n")
    try:
        result = parse_env_file(path)
        assert result == {"EMPTY_KEY": None}
    finally:
        os.unlink(path)


def test_parse_strips_quoted_values():
    path = write_temp_env('QUOTED="hello world"\nSINGLE=\'foo\'\n')
    try:
        result = parse_env_file(path)
        assert result["QUOTED"] == "hello world"
        assert result["SINGLE"] == "foo"
    finally:
        os.unlink(path)


def test_parse_raises_for_missing_file():
    with pytest.raises(FileNotFoundError):
        parse_env_file("/nonexistent/path/.env")


def test_parse_raises_for_invalid_syntax():
    path = write_temp_env("INVALID_LINE_NO_EQUALS\n")
    try:
        with pytest.raises(EnvParseError, match="Invalid syntax on line 1"):
            parse_env_file(path)
    finally:
        os.unlink(path)


def test_parse_raises_for_empty_key():
    path = write_temp_env("=value\n")
    try:
        with pytest.raises(EnvParseError, match="Empty key on line 1"):
            parse_env_file(path)
    finally:
        os.unlink(path)


def test_parse_value_with_equals_sign():
    path = write_temp_env("URL=http://example.com?foo=bar\n")
    try:
        result = parse_env_file(path)
        assert result["URL"] == "http://example.com?foo=bar"
    finally:
        os.unlink(path)
