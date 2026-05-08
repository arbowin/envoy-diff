"""Baseline management: save and compare against a known-good diff result."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy_diff.comparator import DiffResult
from envoy_diff.snapshot import _to_dict, _from_dict


class BaselineError(Exception):
    """Raised when a baseline operation fails."""


class BaselineComparison:
    """Result of comparing a current diff against a saved baseline."""

    def __init__(
        self,
        new_keys: list[str],
        resolved_keys: list[str],
        unchanged_keys: list[str],
    ) -> None:
        self.new_keys = new_keys
        self.resolved_keys = resolved_keys
        self.unchanged_keys = unchanged_keys

    @property
    def has_regressions(self) -> bool:
        return len(self.new_keys) > 0

    @property
    def has_improvements(self) -> bool:
        return len(self.resolved_keys) > 0


def save_baseline(result: DiffResult, path: str | Path) -> None:
    """Persist *result* as a baseline JSON file."""
    dest = Path(path)
    try:
        dest.write_text(json.dumps(_to_dict(result), indent=2), encoding="utf-8")
    except OSError as exc:
        raise BaselineError(f"Cannot write baseline to {dest}: {exc}") from exc


def load_baseline(path: str | Path) -> DiffResult:
    """Load a previously saved baseline from *path*."""
    src = Path(path)
    if not src.exists():
        raise BaselineError(f"Baseline file not found: {src}")
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
        return _from_dict(data)
    except (json.JSONDecodeError, KeyError) as exc:
        raise BaselineError(f"Invalid baseline file {src}: {exc}") from exc


def compare_against_baseline(
    current: DiffResult, baseline: DiffResult
) -> BaselineComparison:
    """Return which diff entries are new, resolved, or unchanged."""
    baseline_keys = {e[0] for e in baseline.differences}
    current_keys = {e[0] for e in current.differences}

    new_keys = sorted(current_keys - baseline_keys)
    resolved_keys = sorted(baseline_keys - current_keys)
    unchanged_keys = sorted(current_keys & baseline_keys)

    return BaselineComparison(
        new_keys=new_keys,
        resolved_keys=resolved_keys,
        unchanged_keys=unchanged_keys,
    )
