"""Tests for envoy_diff.differ_snapshot."""

from __future__ import annotations

import pytest

from envoy_diff.differ_snapshot import diff_and_snapshot, diff_against_snapshot
from envoy_diff.snapshot import load_snapshot, SnapshotError


def _write_env(path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


@pytest.fixture()
def source_file(tmp_path):
    f = tmp_path / "source.env"
    _write_env(f, "KEY_A=hello\nKEY_B=world\n")
    return f


@pytest.fixture()
def target_file(tmp_path):
    f = tmp_path / "target.env"
    _write_env(f, "KEY_A=hello\nKEY_C=extra\n")
    return f


def test_diff_and_snapshot_creates_file(tmp_path, source_file, target_file):
    snap = tmp_path / "snap.json"
    diff_and_snapshot(source_file, target_file, snap)
    assert snap.exists()


def test_diff_and_snapshot_result_persisted(tmp_path, source_file, target_file):
    snap = tmp_path / "snap.json"
    report = diff_and_snapshot(source_file, target_file, snap)
    loaded = load_snapshot(snap)
    assert loaded.missing_in_target == report.result.missing_in_target
    assert loaded.missing_in_source == report.result.missing_in_source


def test_diff_and_snapshot_returns_report(tmp_path, source_file, target_file):
    snap = tmp_path / "snap.json"
    report = diff_and_snapshot(source_file, target_file, snap)
    assert report.result is not None
    assert hasattr(report, "source_path")


def test_diff_against_snapshot_missing_snapshot_raises(tmp_path, source_file):
    with pytest.raises(SnapshotError):
        diff_against_snapshot(source_file, tmp_path / "missing.json")


def test_diff_against_snapshot_returns_report(tmp_path, source_file, target_file):
    snap = tmp_path / "snap.json"
    diff_and_snapshot(source_file, target_file, snap)
    report = diff_against_snapshot(source_file, snap)
    assert report is not None
