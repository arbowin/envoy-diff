"""Tests for envoy_diff.watchdog."""

from __future__ import annotations

import os
import time
import threading
from pathlib import Path

import pytest

from envoy_diff.watchdog import (
    WatchdogOptions,
    WatchEvent,
    WatchdogError,
    watch_pair,
    _mtime,
)


def write_env(path: Path, content: str) -> None:
    path.write_text(content)


def test_mtime_missing_file_returns_zero():
    assert _mtime("/nonexistent/path/file.env") == 0.0


def test_mtime_existing_file_returns_positive(tmp_path):
    f = tmp_path / "a.env"
    f.write_text("KEY=1")
    assert _mtime(str(f)) > 0.0


def test_watch_pair_detects_change(tmp_path):
    src = tmp_path / "source.env"
    tgt = tmp_path / "target.env"
    write_env(src, "KEY=hello\n")
    write_env(tgt, "KEY=hello\n")

    events: list[WatchEvent] = []
    opts = WatchdogOptions(poll_interval=0.05, max_events=1)

    def modify():
        time.sleep(0.1)
        write_env(tgt, "KEY=world\n")

    t = threading.Thread(target=modify, daemon=True)
    t.start()
    watch_pair(str(src), str(tgt), events.append, opts)
    t.join(timeout=2)

    assert len(events) == 1
    assert events[0].path == str(tgt)


def test_watch_pair_event_contains_diff(tmp_path):
    src = tmp_path / "source.env"
    tgt = tmp_path / "target.env"
    write_env(src, "KEY=hello\nEXTRA=yes\n")
    write_env(tgt, "KEY=hello\n")

    events: list[WatchEvent] = []
    opts = WatchdogOptions(poll_interval=0.05, max_events=1)

    def modify():
        time.sleep(0.1)
        write_env(tgt, "KEY=changed\n")

    t = threading.Thread(target=modify, daemon=True)
    t.start()
    watch_pair(str(src), str(tgt), events.append, opts)
    t.join(timeout=2)

    report = events[0].report
    assert report.result.has_differences


def test_watch_pair_stops_after_max_events(tmp_path):
    src = tmp_path / "source.env"
    tgt = tmp_path / "target.env"
    write_env(src, "A=1\n")
    write_env(tgt, "A=1\n")

    events: list[WatchEvent] = []
    opts = WatchdogOptions(poll_interval=0.05, max_events=2)

    def modify():
        for i in range(3):
            time.sleep(0.12)
            write_env(tgt, f"A={i}\n")

    t = threading.Thread(target=modify, daemon=True)
    t.start()
    watch_pair(str(src), str(tgt), events.append, opts)
    t.join(timeout=5)

    assert len(events) == 2
