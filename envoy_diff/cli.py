"""Command-line interface for envoy-diff."""

import argparse
import sys
from pathlib import Path

from envoy_diff.parser import parse_env_file, EnvParseError
from envoy_diff.comparator import compare_envs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envoy-diff",
        description="Compare .env files across environments and flag missing or mismatched keys.",
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Source .env file (reference, e.g. .env.example)",
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Target .env file to compare against source",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any differences are found",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output; only use exit code to signal differences",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    for path in (args.source, args.target):
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 2

    try:
        source_env = parse_env_file(args.source)
        target_env = parse_env_file(args.target)
    except EnvParseError as exc:
        print(f"Error parsing env file: {exc}", file=sys.stderr)
        return 2

    result = compare_envs(source_env, target_env)

    if not args.quiet:
        print(f"Comparing {args.source} -> {args.target}")
        print(result.summary())

    if args.strict and result.has_differences:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
