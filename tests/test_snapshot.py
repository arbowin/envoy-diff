"""Tests for envoy_diff.snapshot."""

from __future__ import annotations

import json
import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.snapshot import (
    SnapshotError,
    load_snapshot,
    save_snapshot,
    snapshot_to_string,
)


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_target=["KEY_A"],
        missing_in_source=["KEY_B"],
        mismatched={"KEY_C": ("val1", "val2")},
        common=["KEY_D"],
    )


def test_snapshot_to_string_is_valid_json(sample_result):
    text = snapshot_to_string(sample_result)
    data = json.loads(text)
    assert data["missing_in_target"] == ["KEY_A"]
    assert data["missing_in_source"] == ["KEY_B"]
    assert data["common"] == ["KEY_D"]
    assert data["_schema"] == 1


def test_save_and_load_round_trip(tmp_path, sample_result):
    dest = tmp_path / "snap.json"
    save_snapshot(sample_result, dest)
    loaded = load_snapshot(dest)
    assert loaded.missing_in_target == sample_result.missing_in_target
    assert loaded.missing_in_source == sample_result.missing_in_source
    assert loaded.mismatched == sample_result.mismatched
    assert loaded.common == sample_result.common


def test_save_creates_file(tmp_path, sample_result):
    dest = tmp_path / "snap.json"
    assert not dest.exists()
    save_snapshot(sample_result, dest)
    assert dest.exists()


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(SnapshotError, match="Could not read snapshot"):
        load_snapshot(tmp_path / "nonexistent.json")


def test_load_invalid_json_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    with pytest.raises(SnapshotError, match="Invalid JSON"):
        load_snapshot(bad)


def test_load_wrong_schema_raises(tmp_path):
    snap = tmp_path / "snap.json"
    data = {
        "_schema": 99,
        "missing_in_target": [],
        "missing_in_source": [],
        "mismatched": {},
        "common": [],
    }
    snap.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(SnapshotError, match="Unsupported snapshot schema version"):
        load_snapshot(snap)


def test_empty_result_round_trip(tmp_path):
    empty = DiffResult(missing_in_target=[], missing_in_source=[], mismatched={}, common=[])
    dest = tmp_path / "empty.json"
    save_snapshot(empty, dest)
    loaded = load_snapshot(dest)
    assert loaded.missing_in_target == []
    assert loaded.mismatched == {}
