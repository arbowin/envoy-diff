"""Command-line interface for envoy-diff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envoy_diff.comparator import compare_envs, has_differences
from envoy_diff.formatter import OutputFormat, format_result
from envoy_diff.parser import EnvParseError, parse_env_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envoy-diff",
        description="Compare .env files across environments and flag missing or mismatched keys.",
    )
    parser.add_argument("source", type=Path, help="Source .env file (baseline)")
    parser.add_argument("target", type=Path, help="Target .env file to compare against")
    parser.add_argument(
        "--format",
        choices=[f.value for f in OutputFormat],
        default=OutputFormat.TEXT.value,
        dest="fmt",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--source-name",
        default=None,
        help="Display name for the source file (default: filename)",
    )
    parser.add_argument(
        "--target-name",
        default=None,
        help="Display name for the target file (default: filename)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if differences are found",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    source_name = args.source_name or args.source.name
    target_name = args.target_name or args.target.name

    try:
        source_env = parse_env_file(args.source)
        target_env = parse_env_file(args.target)
    except EnvParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    result = compare_envs(source_env, target_env)
    fmt = OutputFormat(args.fmt)
    output = format_result(result, fmt=fmt, source_name=source_name, target_name=target_name)
    print(output)

    if args.exit_code and has_differences(result):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
