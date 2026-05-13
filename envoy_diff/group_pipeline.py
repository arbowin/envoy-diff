"""High-level pipeline: parse two .env files, diff, group, and render."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from envoy_diff.comparator import compare_envs
from envoy_diff.group_reporter import render_group
from envoy_diff.grouper import GroupedResult, group_result
from envoy_diff.parser import EnvParseError, parse_env_file


class GroupPipelineError(Exception):
    """Raised when the group pipeline cannot complete."""


@dataclass
class GroupPipelineOutput:
    grouped: GroupedResult
    rendered: str


def run_group_pipeline(
    source: str | Path,
    target: str | Path,
    fmt: str = "text",
    separator: str = "_",
    prefix_filter: Optional[str] = None,
) -> GroupPipelineOutput:
    """Parse *source* and *target*, diff them, group by prefix, and render.

    Parameters
    ----------
    source:
        Path to the source .env file.
    target:
        Path to the target .env file.
    fmt:
        Output format — ``"text"``, ``"json"``, or ``"markdown"``.
    separator:
        Character used to split key prefixes (default ``"_"``).
    prefix_filter:
        If given, only the group with this prefix is included in output.
    """
    try:
        src_env = parse_env_file(str(source))
        tgt_env = parse_env_file(str(target))
    except EnvParseError as exc:
        raise GroupPipelineError(str(exc)) from exc

    diff = compare_envs(src_env, tgt_env)
    grouped = group_result(diff, separator=separator)

    if prefix_filter is not None:
        key = prefix_filter.upper()
        if key not in grouped.groups:
            raise GroupPipelineError(
                f"Prefix '{key}' not found. Available: {grouped.group_names}"
            )
        from envoy_diff.grouper import GroupedResult as GR

        filtered = GR(separator=separator)
        filtered.groups[key] = grouped.groups[key]
        grouped = filtered

    rendered = render_group(grouped, fmt=fmt)
    return GroupPipelineOutput(grouped=grouped, rendered=rendered)
