"""Audit trail: record and replay diff operations with timestamps."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from envoy_diff.comparator import DiffResult
from envoy_diff.snapshot import _to_dict, _from_dict


class AuditError(Exception):
    """Raised when an audit operation fails."""


@dataclass
class AuditEntry:
    """A single recorded diff operation."""

    timestamp: str
    source_path: str
    target_path: str
    result: DiffResult
    note: Optional[str] = None


@dataclass
class AuditLog:
    """Collection of audit entries."""

    entries: List[AuditEntry] = field(default_factory=list)

    def add(self, entry: AuditEntry) -> None:
        self.entries.append(entry)

    def __len__(self) -> int:
        return len(self.entries)


def _entry_to_dict(entry: AuditEntry) -> dict:
    return {
        "timestamp": entry.timestamp,
        "source_path": entry.source_path,
        "target_path": entry.target_path,
        "result": _to_dict(entry.result),
        "note": entry.note,
    }


def _entry_from_dict(data: dict) -> AuditEntry:
    return AuditEntry(
        timestamp=data["timestamp"],
        source_path=data["source_path"],
        target_path=data["target_path"],
        result=_from_dict(data["result"]),
        note=data.get("note"),
    )


def record_audit(
    source_path: str,
    target_path: str,
    result: DiffResult,
    note: Optional[str] = None,
) -> AuditEntry:
    """Create a new audit entry with the current UTC timestamp."""
    ts = datetime.now(timezone.utc).isoformat()
    return AuditEntry(
        timestamp=ts,
        source_path=source_path,
        target_path=target_path,
        result=result,
        note=note,
    )


def save_audit_log(log: AuditLog, path: str) -> None:
    """Persist an audit log to a JSON file."""
    try:
        data = [_entry_to_dict(e) for e in log.entries]
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError as exc:
        raise AuditError(f"Failed to write audit log: {exc}") from exc


def load_audit_log(path: str) -> AuditLog:
    """Load an audit log from a JSON file."""
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise AuditError(f"Failed to read audit log: {exc}") from exc
    try:
        data = json.loads(raw)
        entries = [_entry_from_dict(d) for d in data]
        return AuditLog(entries=entries)
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise AuditError(f"Corrupt audit log: {exc}") from exc
