"""Snapshot module: save and load DiffResult snapshots for later comparison."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Union

from envoy_diff.comparator import DiffResult


class SnapshotError(Exception):
    """Raised when a snapshot operation fails."""


_SCHEMA_VERSION = 1


def _to_dict(result: DiffResult) -> dict:
    data = asdict(result)
    data["_schema"] = _SCHEMA_VERSION
    return data


def _from_dict(data: dict) -> DiffResult:
    schema = data.pop("_schema", None)
    if schema != _SCHEMA_VERSION:
        raise SnapshotError(
            f"Unsupported snapshot schema version: {schema!r} (expected {_SCHEMA_VERSION})"
        )
    return DiffResult(
        missing_in_target=data.get("missing_in_target", []),
        missing_in_source=data.get("missing_in_source", []),
        mismatched=data.get("mismatched", {}),
        common=data.get("common", []),
    )


def save_snapshot(result: DiffResult, path: Union[str, Path]) -> None:
    """Serialise *result* to a JSON snapshot file at *path*."""
    dest = Path(path)
    try:
        dest.write_text(json.dumps(_to_dict(result), indent=2), encoding="utf-8")
    except OSError as exc:
        raise SnapshotError(f"Could not write snapshot to {dest}: {exc}") from exc


def load_snapshot(path: Union[str, Path]) -> DiffResult:
    """Deserialise a DiffResult from a JSON snapshot file at *path*."""
    src = Path(path)
    try:
        raw = src.read_text(encoding="utf-8")
    except OSError as exc:
        raise SnapshotError(f"Could not read snapshot from {src}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SnapshotError(f"Invalid JSON in snapshot {src}: {exc}") from exc
    return _from_dict(data)


def snapshot_to_string(result: DiffResult) -> str:
    """Return the snapshot JSON as a string without writing to disk."""
    return json.dumps(_to_dict(result), indent=2)
