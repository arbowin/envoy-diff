"""envoy-diff: Compare .env files across environments and flag missing or mismatched keys."""

from __future__ import annotations

from envoy_diff.comparator import DiffResult, compare_envs, has_differences, summary
from envoy_diff.formatter import OutputFormat, format_result
from envoy_diff.parser import EnvParseError, parse_env_file
from envoy_diff.reporter import ReportError, report_to_string, write_report

__all__ = [
    # parser
    "EnvParseError",
    "parse_env_file",
    # comparator
    "DiffResult",
    "compare_envs",
    "has_differences",
    "summary",
    # formatter
    "OutputFormat",
    "format_result",
    # reporter
    "ReportError",
    "report_to_string",
    "write_report",
]

__version__ = "0.1.0"
