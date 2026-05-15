"""High-level pipeline that wires together watching, diffing, and reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from envoy_diff.differ import DiffOptions
from envoy_diff.watchdog import WatchdogOptions, WatchEvent, watch_pair
from envoy_diff.watchdog_reporter import render_watch


class WatchPipelineError(Exception):
    """Raised for configuration or runtime errors in the watch pipeline."""


@dataclass
class WatchPipelineOptions:
    """Options for the watch pipeline."""

    fmt: str = "text"
    poll_interval: float = 1.0
    max_events: Optional[int] = None
    diff_options: DiffOptions = field(default_factory=DiffOptions)


@dataclass
class WatchPipelineOutput:
    """Accumulates rendered output for each event."""

    events: List[str] = field(default_factory=list)

    def add(self, rendered: str) -> None:
        self.events.append(rendered)

    @property
    def event_count(self) -> int:
        return len(self.events)


def run_watch_pipeline(
    source: str,
    target: str,
    on_event: Optional[Callable[[str], None]] = None,
    options: Optional[WatchPipelineOptions] = None,
) -> WatchPipelineOutput:
    """Start watching *source* and *target*, rendering each change event.

    If *on_event* is provided it is called with the rendered string for every
    detected change.  All rendered strings are also collected in the returned
    :class:`WatchPipelineOutput`.
    """
    if options is None:
        options = WatchPipelineOptions()

    output = WatchPipelineOutput()
    watchdog_opts = WatchdogOptions(
        poll_interval=options.poll_interval,
        diff_options=options.diff_options,
        max_events=options.max_events,
    )

    def _handle(event: WatchEvent) -> None:
        rendered = render_watch(event, fmt=options.fmt)
        output.add(rendered)
        if on_event is not None:
            on_event(rendered)

    watch_pair(source, target, _handle, watchdog_opts)
    return output
