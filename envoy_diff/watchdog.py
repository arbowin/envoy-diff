"""Watch .env files for changes and report diffs on modification."""

from __future__ import annotations

import time
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Optional

from envoy_diff.differ import DiffOptions, DiffReport, diff_files


class WatchdogError(Exception):
    """Raised when the watchdog encounters an unrecoverable error."""


@dataclass
class WatchEvent:
    """Describes a single file-change event and the resulting diff."""

    path: str
    previous_mtime: float
    current_mtime: float
    report: DiffReport


@dataclass
class WatchdogOptions:
    """Configuration for the file watcher."""

    poll_interval: float = 1.0
    diff_options: DiffOptions = field(default_factory=DiffOptions)
    max_events: Optional[int] = None  # None means run forever


def _mtime(path: str) -> float:
    """Return the modification time of *path*, or 0.0 if it does not exist."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


def watch_pair(
    source: str,
    target: str,
    callback: Callable[[WatchEvent], None],
    options: Optional[WatchdogOptions] = None,
) -> None:
    """Poll *source* and *target* and invoke *callback* whenever either changes.

    Blocks until *options.max_events* events have been emitted (or forever if
    ``max_events`` is ``None``).
    """
    if options is None:
        options = WatchdogOptions()

    mtimes: Dict[str, float] = {
        source: _mtime(source),
        target: _mtime(target),
    }
    events_emitted = 0

    while True:
        time.sleep(options.poll_interval)
        changed = False
        for path in (source, target):
            current = _mtime(path)
            if current != mtimes[path]:
                changed = True
                mtimes[path] = current

        if changed:
            try:
                report = diff_files(source, target, options.diff_options)
            except Exception as exc:  # pragma: no cover
                raise WatchdogError(f"diff failed: {exc}") from exc

            event = WatchEvent(
                path=target,
                previous_mtime=mtimes[target],
                current_mtime=_mtime(target),
                report=report,
            )
            callback(event)
            events_emitted += 1
            if options.max_events is not None and events_emitted >= options.max_events:
                break
