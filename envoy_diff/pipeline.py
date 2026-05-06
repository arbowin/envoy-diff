"""Pipeline module for envoy-diff.

Orchestrates parsing, optional validation, comparison, filtering,
sorting, and formatting into a single callable entry point.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envoy_diff.comparator import compare_envs
from envoy_diff.filter import FilterOptions, filter_result
from envoy_diff.formatter import OutputFormat, format_result
from envoy_diff.parser import parse_env_file
from envoy_diff.sorter import SortKey, sort_result
from envoy_diff.validator import ValidationWarning, validate_env


@dataclass
class PipelineOptions:
    source_path: Path
    target_path: Path
    output_format: OutputFormat = OutputFormat.TEXT
    sort_key: SortKey = SortKey.KEY
    sort_reverse: bool = False
    filter_options: FilterOptions = field(default_factory=FilterOptions)
    validate: bool = False


@dataclass
class PipelineOutput:
    formatted: str
    validation_warnings: List[ValidationWarning] = field(default_factory=list)


def run_pipeline(options: PipelineOptions) -> PipelineOutput:
    """Execute the full envoy-diff pipeline and return formatted output.

    Steps:
    1. Parse source and target .env files.
    2. Optionally validate both files and collect warnings.
    3. Compare the two parsed environments.
    4. Filter the diff result.
    5. Sort the diff result.
    6. Format and return the result.
    """
    source_env = parse_env_file(options.source_path)
    target_env = parse_env_file(options.target_path)

    warnings: List[ValidationWarning] = []
    if options.validate:
        for env in (source_env, target_env):
            vr = validate_env(env)
            warnings.extend(vr.warnings)

    diff = compare_envs(source_env, target_env)
    diff = filter_result(diff, options.filter_options)
    diff = sort_result(diff, key=options.sort_key, reverse=options.sort_reverse)

    formatted = format_result(diff, options.output_format)
    return PipelineOutput(formatted=formatted, validation_warnings=warnings)
