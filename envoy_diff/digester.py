"""Compute and compare content digests (hashes) for .env files."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from envoy_diff.parser import parse_env_file


class DigestError(Exception):
    """Raised when a digest operation fails."""


@dataclass
class DigestEntry:
    """Digest information for a single .env file."""

    path: str
    key_count: int
    digest: str  # hex SHA-256 of sorted key=value pairs

    def as_dict(self) -> Dict[str, object]:
        return {"path": self.path, "key_count": self.key_count, "digest": self.digest}


@dataclass
class DigestComparison:
    """Result of comparing two DigestEntry objects."""

    source: DigestEntry
    target: DigestEntry
    match: bool = field(init=False)

    def __post_init__(self) -> None:
        self.match = self.source.digest == self.target.digest


def _compute_digest(env: Dict[str, Optional[str]]) -> str:
    """Return a deterministic SHA-256 hex digest for *env*."""
    canonical = json.dumps(
        {k: env[k] for k in sorted(env)}, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def digest_file(path: str | Path) -> DigestEntry:
    """Parse *path* and return a :class:`DigestEntry`.

    Raises :class:`DigestError` if the file cannot be read or parsed.
    """
    try:
        env = parse_env_file(str(path))
    except Exception as exc:  # noqa: BLE001
        raise DigestError(f"Failed to digest '{path}': {exc}") from exc

    return DigestEntry(
        path=str(path),
        key_count=len(env),
        digest=_compute_digest(env),
    )


def compare_digests(source: str | Path, target: str | Path) -> DigestComparison:
    """Digest both files and return a :class:`DigestComparison`."""
    return DigestComparison(
        source=digest_file(source),
        target=digest_file(target),
    )
