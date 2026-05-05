"""Tests for envoy_diff.sorter."""

import pytest

from envoy_diff.comparator import DiffResult
from envoy_diff.sorter import SortKey, sort_result


@pytest.fixture()
def mixed_result() -> DiffResult:
    return DiffResult(
        differences=[
            {"key": "ZEBRA", "source_value": "z", "target_value": None},   # missing_in_target
            {"key": "ALPHA", "source_value": "a", "target_value": "b"},    # mismatch
            {"key": "MANGO", "source_value": None, "target_value": "m"},   # missing_in_source
            {"key": "BERRY", "source_value": "x", "target_value": None},   # missing_in_target
        ],
        source_only=["ZEBRA", "BERRY"],
        target_only=["MANGO"],
    )


def test_sort_by_key_ascending(mixed_result):
    sorted_result = sort_result(mixed_result, sort_by=SortKey.KEY)
    keys = [e["key"] for e in sorted_result.differences]
    assert keys == ["ALPHA", "BERRY", "MANGO", "ZEBRA"]


def test_sort_by_key_descending(mixed_result):
    sorted_result = sort_result(mixed_result, sort_by=SortKey.KEY, reverse=True)
    keys = [e["key"] for e in sorted_result.differences]
    assert keys == ["ZEBRA", "MANGO", "BERRY", "ALPHA"]


def test_sort_by_status(mixed_result):
    sorted_result = sort_result(mixed_result, sort_by=SortKey.STATUS)
    statuses = []
    for e in sorted_result.differences:
        if e["source_value"] is None:
            statuses.append("missing_in_source")
        elif e["target_value"] is None:
            statuses.append("missing_in_target")
        else:
            statuses.append("mismatch")
    # missing_in_target entries come first, then missing_in_source, then mismatch
    assert statuses[0] in ("missing_in_target",)
    assert statuses[-1] == "mismatch"


def test_sort_does_not_mutate_original(mixed_result):
    original_keys = [e["key"] for e in mixed_result.differences]
    sort_result(mixed_result, sort_by=SortKey.KEY)
    assert [e["key"] for e in mixed_result.differences] == original_keys


def test_sort_preserves_source_and_target_only(mixed_result):
    sorted_result = sort_result(mixed_result, sort_by=SortKey.KEY)
    assert sorted_result.source_only == mixed_result.source_only
    assert sorted_result.target_only == mixed_result.target_only


def test_sort_empty_differences():
    empty = DiffResult(differences=[], source_only=[], target_only=[])
    sorted_result = sort_result(empty, sort_by=SortKey.KEY)
    assert sorted_result.differences == []
