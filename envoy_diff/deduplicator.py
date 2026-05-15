"""Deduplicator: detect and report duplicate keys across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envoy_diff.parser import parse_env_file, EnvParseError


class DeduplicatorError(Exception):
    """Raised when deduplication cannot be performed."""


@dataclass
class DuplicateEntry:
    """A key that appears in more than one file."""

    key: str
    files: List[str]  # paths where the key was found

    @property
    def count(self) -> int:
        return len(self.files)


@dataclass
class DeduplicationResult:
    """Result of scanning multiple env files for duplicate keys."""

    scanned_files: List[str] = field(default_factory=list)
    duplicates: List[DuplicateEntry] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return len(self.duplicates) > 0

    @property
    def duplicate_keys(self) -> List[str]:
        return [d.key for d in self.duplicates]


def find_duplicates(paths: List[str]) -> DeduplicationResult:
    """Scan *paths* and return every key that appears in more than one file.

    Args:
        paths: List of .env file paths to scan.

    Returns:
        A :class:`DeduplicationResult` describing all cross-file duplicates.

    Raises:
        DeduplicatorError: If any file cannot be read or parsed.
    """
    if not paths:
        return DeduplicationResult(scanned_files=[])

    # key -> list of file paths that contain it
    key_to_files: Dict[str, List[str]] = {}

    for path in paths:
        if not Path(path).exists():
            raise DeduplicatorError(f"File not found: {path}")
        try:
            env = parse_env_file(path)
        except EnvParseError as exc:
            raise DeduplicatorError(f"Failed to parse {path}: {exc}") from exc

        for key in env:
            key_to_files.setdefault(key, []).append(path)

    duplicates = [
        DuplicateEntry(key=key, files=files)
        for key, files in sorted(key_to_files.items())
        if len(files) > 1
    ]

    return DeduplicationResult(scanned_files=list(paths), duplicates=duplicates)
