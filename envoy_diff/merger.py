"""Merge multiple .env files into a single resolved key-value mapping.

Later files take precedence over earlier ones (last-write-wins).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from envoy_diff.parser import EnvParseError, parse_env_file


class MergeError(Exception:
    """Raised when merging fails due to a parse or I/O problem."""


@dataclass
class MergeResult:
    """Outcome of merging several env files."""

    merged: Dict[str, Optional[str]] = field(default_factory=dict)
    # maps each key to the path that "won" (last file that defined it)
    sources: Dict[str, Path] = field(default_factory=dict)
    # keys that appeared in more than one file
    overridden: List[str] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.merged)


def merge_env_files(paths: Sequence[Path]) -> MergeResult:
    """Merge *paths* in order; later files override earlier ones.

    Parameters
    ----------
    paths:
        Ordered sequence of .env file paths to merge.

    Returns
    -------
    MergeResult
        The combined key-value mapping plus provenance metadata.

    Raises
    ------
    MergeError
        If any file cannot be read or parsed.
    """
    if not paths:
        return MergeResult()

    result = MergeResult()

    for path in paths:
        try:
            env = parse_env_file(path)
        except (EnvParseError, OSError) as exc:
            raise MergeError(f"Failed to read '{path}': {exc}") from exc

        for key, value in env.items():
            if key in result.merged and key not in result.overridden:
                result.overridden.append(key)
            result.merged[key] = value
            result.sources[key] = path

    return result
