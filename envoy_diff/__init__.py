"""envoy-diff: compare .env files across environments."""

from envoy_diff.comparator import DiffResult, compare_envs, has_differences, summary
from envoy_diff.differ import DiffError, DiffOptions, DiffReport, diff_files
from envoy_diff.exporter import ExportError, ExportFormat, export_result
from envoy_diff.filter import FilterOptions, filter_result
from envoy_diff.formatter import OutputFormat, format_result
from envoy_diff.parser import EnvParseError, parse_env_file
from envoy_diff.pipeline import PipelineOptions, PipelineOutput, run_pipeline
from envoy_diff.reporter import ReportError, report_to_string, write_report
from envoy_diff.sorter import SortKey, sort_result
from envoy_diff.validator import ValidationError, ValidationResult, ValidationWarning
from envoy_diff.writer import WriterError, export_to_string, write_export

__all__ = [
    # parser
    "EnvParseError", "parse_env_file",
    # comparator
    "DiffResult", "compare_envs", "has_differences", "summary",
    # differ
    "DiffError", "DiffOptions", "DiffReport", "diff_files",
    # formatter
    "OutputFormat", "format_result",
    # reporter
    "ReportError", "report_to_string", "write_report",
    # filter
    "FilterOptions", "filter_result",
    # sorter
    "SortKey", "sort_result",
    # validator
    "ValidationError", "ValidationResult", "ValidationWarning",
    # pipeline
    "PipelineOptions", "PipelineOutput", "run_pipeline",
    # exporter
    "ExportError", "ExportFormat", "export_result",
    # writer
    "WriterError", "export_to_string", "write_export",
]

__version__ = "0.1.0"
