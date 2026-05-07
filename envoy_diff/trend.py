"""Track and compare diff scores over time to identify environment drift trends."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from envoy_diff.scorer import ScoreResult


class TrendError(Exception):
    """Raised when trend data cannot be read or written."""


@dataclass
class TrendEntry:
    timestamp: str
    score: float
    grade: str
    missing_in_target: int
    missing_in_source: int
    mismatched: int
    label: Optional[str] = None


@dataclass
class TrendLog:
    entries: List[TrendEntry] = field(default_factory=list)

    def add(self, entry: TrendEntry) -> None:
        self.entries.append(entry)

    def __len__(self) -> int:
        return len(self.entries)

    def latest(self) -> Optional[TrendEntry]:
        return self.entries[-1] if self.entries else None

    def delta(self) -> Optional[float]:
        """Return score change between the last two entries, or None."""
        if len(self.entries) < 2:
            return None
        return round(self.entries[-1].score - self.entries[-2].score, 2)


def _entry_from_score(result: ScoreResult, label: Optional[str] = None) -> TrendEntry:
    ts = datetime.now(timezone.utc).isoformat()
    return TrendEntry(
        timestamp=ts,
        score=result.score,
        grade=result.grade,
        missing_in_target=result.missing_in_target,
        missing_in_source=result.missing_in_source,
        mismatched=result.mismatched,
        label=label,
    )


def record_trend(path: Path, result: ScoreResult, label: Optional[str] = None) -> TrendLog:
    """Append a new score entry to the trend log at *path* and return the updated log."""
    log = load_trend(path) if path.exists() else TrendLog()
    log.add(_entry_from_score(result, label=label))
    try:
        path.write_text(json.dumps([e.__dict__ for e in log.entries], indent=2), encoding="utf-8")
    except OSError as exc:
        raise TrendError(f"Cannot write trend log: {exc}") from exc
    return log


def load_trend(path: Path) -> TrendLog:
    """Load a trend log from *path*."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise TrendError(f"Cannot read trend log: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise TrendError(f"Invalid trend log JSON: {exc}") from exc
    return TrendLog(entries=[TrendEntry(**e) for e in raw])
