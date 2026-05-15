"""Tests for envoy_diff.digester and envoy_diff.digest_reporter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envoy_diff.digester import (
    DigestComparison,
    DigestEntry,
    DigestError,
    compare_digests,
    digest_file,
)
from envoy_diff.digest_reporter import (
    format_digest_json,
    format_digest_markdown,
    format_digest_text,
    render_digest,
)


def write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# digester
# ---------------------------------------------------------------------------

def test_digest_file_returns_entry(tmp_path: Path) -> None:
    f = write_env(tmp_path, "a.env", "FOO=bar\nBAZ=qux\n")
    entry = digest_file(f)
    assert isinstance(entry, DigestEntry)
    assert entry.key_count == 2
    assert len(entry.digest) == 64  # SHA-256 hex


def test_digest_file_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(DigestError):
        digest_file(tmp_path / "nonexistent.env")


def test_identical_files_have_same_digest(tmp_path: Path) -> None:
    content = "FOO=bar\nBAZ=qux\n"
    a = write_env(tmp_path, "a.env", content)
    b = write_env(tmp_path, "b.env", content)
    assert digest_file(a).digest == digest_file(b).digest


def test_different_files_have_different_digest(tmp_path: Path) -> None:
    a = write_env(tmp_path, "a.env", "FOO=bar\n")
    b = write_env(tmp_path, "b.env", "FOO=baz\n")
    assert digest_file(a).digest != digest_file(b).digest


def test_digest_is_order_independent(tmp_path: Path) -> None:
    a = write_env(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = write_env(tmp_path, "b.env", "BAR=2\nFOO=1\n")
    assert digest_file(a).digest == digest_file(b).digest


def test_compare_digests_match(tmp_path: Path) -> None:
    content = "KEY=value\n"
    a = write_env(tmp_path, "a.env", content)
    b = write_env(tmp_path, "b.env", content)
    cmp = compare_digests(a, b)
    assert isinstance(cmp, DigestComparison)
    assert cmp.match is True


def test_compare_digests_mismatch(tmp_path: Path) -> None:
    a = write_env(tmp_path, "a.env", "KEY=one\n")
    b = write_env(tmp_path, "b.env", "KEY=two\n")
    cmp = compare_digests(a, b)
    assert cmp.match is False


# ---------------------------------------------------------------------------
# digest_reporter
# ---------------------------------------------------------------------------

@pytest.fixture()
def match_cmp(tmp_path: Path) -> DigestComparison:
    content = "X=1\nY=2\n"
    a = write_env(tmp_path, "src.env", content)
    b = write_env(tmp_path, "tgt.env", content)
    return compare_digests(a, b)


@pytest.fixture()
def diff_cmp(tmp_path: Path) -> DigestComparison:
    a = write_env(tmp_path, "src.env", "X=1\n")
    b = write_env(tmp_path, "tgt.env", "X=99\n")
    return compare_digests(a, b)


def test_text_match_contains_match(match_cmp: DigestComparison) -> None:
    assert "MATCH" in format_digest_text(match_cmp)


def test_text_mismatch_contains_mismatch(diff_cmp: DigestComparison) -> None:
    assert "MISMATCH" in format_digest_text(diff_cmp)


def test_json_is_valid_and_has_match_key(match_cmp: DigestComparison) -> None:
    data = json.loads(format_digest_json(match_cmp))
    assert data["match"] is True
    assert "source" in data and "target" in data


def test_markdown_contains_table(diff_cmp: DigestComparison) -> None:
    md = format_digest_markdown(diff_cmp)
    assert "|" in md
    assert "MISMATCH" in md


def test_render_digest_delegates_format(match_cmp: DigestComparison) -> None:
    assert render_digest(match_cmp, "json").startswith("{")
    assert render_digest(match_cmp, "markdown").startswith("##")
    assert "MATCH" in render_digest(match_cmp, "text")
