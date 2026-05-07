"""Profile .env files to produce summary statistics."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envoy_diff.parser import parse_env_file, EnvParseError


@dataclass
class ProfileResult:
    """Summary statistics for a single .env file."""

    path: str
    total_keys: int = 0
    empty_values: int = 0
    non_empty_values: int = 0
    duplicate_keys: List[str] = field(default_factory=list)
    longest_key: str = ""
    longest_value_key: str = ""
    unique_prefixes: List[str] = field(default_factory=list)

    @property
    def empty_ratio(self) -> float:
        """Fraction of keys that have empty/None values."""
        if self.total_keys == 0:
            return 0.0
        return self.empty_values / self.total_keys


class ProfileError(Exception):
    """Raised when profiling fails."""


def profile_env_file(path: str | Path) -> ProfileResult:
    """Parse *path* and compute summary statistics.

    Parameters
    ----------
    path:
        Path to the .env file to profile.

    Returns
    -------
    ProfileResult
        Populated statistics object.

    Raises
    ------
    ProfileError
        If the file cannot be read or parsed.
    """
    path = Path(path)
    try:
        env: Dict[str, str | None] = parse_env_file(path)
    except (EnvParseError, OSError) as exc:
        raise ProfileError(f"Cannot profile '{path}': {exc}") from exc

    result = ProfileResult(path=str(path))

    seen_keys: Dict[str, int] = {}
    prefix_set: set[str] = set()
    longest_key_len = 0
    longest_val_len = -1

    for key, value in env.items():
        seen_keys[key] = seen_keys.get(key, 0) + 1
        result.total_keys += 1

        if value is None or value == "":
            result.empty_values += 1
        else:
            result.non_empty_values += 1

        if len(key) > longest_key_len:
            longest_key_len = len(key)
            result.longest_key = key

        val_len = len(value) if value else 0
        if val_len > longest_val_len:
            longest_val_len = val_len
            result.longest_value_key = key

        if "_" in key:
            prefix_set.add(key.split("_", 1)[0])

    result.duplicate_keys = [k for k, count in seen_keys.items() if count > 1]
    result.unique_prefixes = sorted(prefix_set)
    return result
