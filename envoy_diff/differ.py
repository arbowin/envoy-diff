"""High-level diff orchestration: parse, validate, compare, and filter in one call."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .parser import parse_env_file, EnvParseError
from .comparator import compare_envs, DiffResult
from .validator import validate_env, ValidationResult
from .filter import FilterOptions, filter_result
from .sorter import SortKey, sort_result


@dataclass
class DiffOptions:
    """Options controlling how a diff is performed."""
    filter: Optional[FilterOptions] = None
    sort_by: SortKey = SortKey.KEY
    sort_descending: bool = False
    validate: bool = True


@dataclass
class DiffReport:
    """Full output of a diff operation."""
    result: DiffResult
    source_validation: Optional[ValidationResult] = None
    target_validation: Optional[ValidationResult] = None
    source_path: str = ""
    target_path: str = ""


class DiffError(Exception):
    """Raised when the diff operation cannot be completed."""


def diff_files(
    source: Path,
    target: Path,
    options: Optional[DiffOptions] = None,
) -> DiffReport:
    """Parse two .env files and return a DiffReport.

    Args:
        source: Path to the source .env file.
        target: Path to the target .env file.
        options: Optional DiffOptions controlling filtering, sorting, and validation.

    Returns:
        A DiffReport containing the comparison result and optional validation info.

    Raises:
        DiffError: If either file cannot be parsed.
    """
    if options is None:
        options = DiffOptions()

    try:
        source_env = parse_env_file(source)
    except (EnvParseError, OSError) as exc:
        raise DiffError(f"Failed to parse source file '{source}': {exc}") from exc

    try:
        target_env = parse_env_file(target)
    except (EnvParseError, OSError) as exc:
        raise DiffError(f"Failed to parse target file '{target}': {exc}") from exc

    source_validation = validate_env(source_env) if options.validate else None
    target_validation = validate_env(target_env) if options.validate else None

    result = compare_envs(source_env, target_env)

    if options.filter is not None:
        result = filter_result(result, options.filter)

    result = sort_result(result, options.sort_by, options.sort_descending)

    return DiffReport(
        result=result,
        source_validation=source_validation,
        target_validation=target_validation,
        source_path=str(source),
        target_path=str(target),
    )
