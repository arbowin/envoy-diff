"""Classify diff entries into semantic categories based on key naming conventions."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

from envoy_diff.comparator import DiffResult


class KeyCategory(str, Enum):
    DATABASE = "database"
    AUTH = "auth"
    NETWORK = "network"
    FEATURE_FLAG = "feature_flag"
    LOGGING = "logging"
    STORAGE = "storage"
    OTHER = "other"


_PATTERNS: List[tuple[KeyCategory, List[str]]] = [
    (KeyCategory.DATABASE, ["DB_", "DATABASE_", "POSTGRES", "MYSQL", "MONGO", "REDIS"]),
    (KeyCategory.AUTH, ["AUTH_", "JWT_", "SECRET", "TOKEN", "PASSWORD", "API_KEY", "OAUTH"]),
    (KeyCategory.NETWORK, ["HOST", "PORT", "URL", "ENDPOINT", "BASE_URL", "PROXY"]),
    (KeyCategory.FEATURE_FLAG, ["FEATURE_", "FLAG_", "ENABLE_", "DISABLE_", "FF_"]),
    (KeyCategory.LOGGING, ["LOG_", "LOGGING_", "SENTRY_", "DEBUG", "VERBOSE"]),
    (KeyCategory.STORAGE, ["S3_", "BUCKET_", "STORAGE_", "GCS_", "BLOB_"]),
]


@dataclass
class ClassifiedResult:
    source_path: str
    target_path: str
    categories: Dict[KeyCategory, List[str]] = field(default_factory=dict)

    def keys_in(self, category: KeyCategory) -> List[str]:
        return self.categories.get(category, [])

    def all_categories(self) -> List[KeyCategory]:
        return [c for c in KeyCategory if c in self.categories and self.categories[c]]


def _categorize_key(key: str) -> KeyCategory:
    upper = key.upper()
    for category, prefixes in _PATTERNS:
        if any(upper.startswith(p) or p in upper for p in prefixes):
            return category
    return KeyCategory.OTHER


def classify_result(result: DiffResult) -> ClassifiedResult:
    """Classify all keys in a DiffResult into semantic categories."""
    classified = ClassifiedResult(
        source_path=result.source_path,
        target_path=result.target_path,
    )
    all_keys = (
        list(result.missing_in_target)
        + list(result.missing_in_source)
        + list(result.mismatched.keys())
        + list(result.matching.keys())
    )
    for key in all_keys:
        cat = _categorize_key(key)
        classified.categories.setdefault(cat, []).append(key)
    for cat in classified.categories:
        classified.categories[cat].sort()
    return classified
