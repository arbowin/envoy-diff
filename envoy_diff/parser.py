"""Parser module for reading and parsing .env files."""

import os
from typing import Dict, Optional


class EnvParseError(Exception):
    """Raised when an .env file cannot be parsed."""
    pass


def parse_env_file(filepath: str) -> Dict[str, Optional[str]]:
    """Parse a .env file and return a dictionary of key-value pairs.

    Args:
        filepath: Path to the .env file.

    Returns:
        A dict mapping environment variable names to their values.
        Keys without values are mapped to None.

    Raises:
        FileNotFoundError: If the file does not exist.
        EnvParseError: If the file contains invalid syntax.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    env_vars: Dict[str, Optional[str]] = {}

    with open(filepath, "r", encoding="utf-8") as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = raw_line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                raise EnvParseError(
                    f"Invalid syntax on line {line_number}: '{line}'"
                )

            key, _, value = line.partition("=")
            key = key.strip()

            if not key:
                raise EnvParseError(
                    f"Empty key on line {line_number}: '{line}'"
                )

            value = value.strip()

            # Strip surrounding quotes if present
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]

            env_vars[key] = value if value else None

    return env_vars
