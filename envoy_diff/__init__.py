"""envoy-diff: compare .env files across environments."""

from envoy_diff.comparator import DiffResult, compare_envs, has_differences, summary
from envoy_diff.differ import DiffError, DiffOptions, DiffReport, diff_files
from envoy_diff.filter import FilterOptions, filter_result
from envoy_diff.formatter import OutputFormat, format_result
from envoy_diff.merger import MergeError, MergeResult, merge_env_files
from envoy_diff.parser import EnvParseError, parse_env_file
from envoy_diff.patcher import PatchResult, generate_patch
from envoy_diff.pipeline import PipelineOptions, PipelineOutput, run_pipeline
from envoy_diff.reporter import ReportError, report_to_string, write_report
from envoy_diff.snapshot import SnapshotError, load_snapshot, save_snapshot, snapshot_to_string
from envoy_diff.sorter import SortKey, sort_result
from envoy_diff.validator import ValidationResult, is_valid
from envoy_diff.writer import WriterError, export_to_string, write_export

__all__ = [
    # comparator
    "DiffResult",
    "compare_envs",
    "has_differences",
    "summary",
    # differ
    "DiffError",
    "DiffOptions",
    "DiffReport",
    "diff_files",
    # filter
    "FilterOptions",
    "filter_result",
    # formatter
    "OutputFormat",
    "format_result",
    # merger
    "MergeError",
    "MergeResult",
    "merge_env_files",
    # parser
    "EnvParseError",
    "parse_env_file",
    # patcher
    "PatchResult",
    "generate_patch",
    # pipeline
    "PipelineOptions",
    "PipelineOutput",
    "run_pipeline",
    # reporter
    "ReportError",
    "report_to_string",
    "write_report",
    # snapshot
    "SnapshotError",
    "load_snapshot",
    "save_snapshot",
    "snapshot_to_string",
    # sorter
    "SortKey",
    "sort_result",
    # validator
    "ValidationResult",
    "is_valid",
    # writer
    "WriterError",
    "export_to_string",
    "write_export",
]
