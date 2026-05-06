"""Lint .env files for common style and correctness issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class LintSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintIssue:
    line: int
    key: Optional[str]
    message: str
    severity: LintSeverity

    def __str__(self) -> str:
        location = f"line {self.line}" + (f" ({self.key})" if self.key else "")
        return f"[{self.severity.value.upper()}] {location}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == LintSeverity.ERROR]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == LintSeverity.WARNING]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def add(self, issue: LintIssue) -> None:
        self.issues.append(issue)


def lint_env_file(path: str) -> LintResult:
    """Lint a single .env file and return a LintResult."""
    result = LintResult()
    seen_keys: Dict[str, int] = {}

    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        if not line or line.lstrip().startswith("#"):
            continue

        if "=" not in line:
            result.add(LintIssue(lineno, None, "Line has no '=' separator", LintSeverity.ERROR))
            continue

        key, _, value = line.partition("=")
        key = key.strip()

        if not key:
            result.add(LintIssue(lineno, None, "Empty key", LintSeverity.ERROR))
            continue

        if key in seen_keys:
            result.add(LintIssue(
                lineno, key,
                f"Duplicate key (first seen at line {seen_keys[key]})",
                LintSeverity.WARNING,
            ))
        else:
            seen_keys[key] = lineno

        if key != key.upper():
            result.add(LintIssue(lineno, key, "Key is not uppercase", LintSeverity.INFO))

        if value != value.strip() and not (value.startswith('"') or value.startswith("'")):
            result.add(LintIssue(lineno, key, "Value has leading or trailing whitespace", LintSeverity.WARNING))

        if len(line) > 200:
            result.add(LintIssue(lineno, key, "Line exceeds 200 characters", LintSeverity.INFO))

    return result
