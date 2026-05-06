"""Apply a PatchResult to an existing env mapping to produce a patched mapping."""

from __future__ import annotations

from typing import Dict, Optional

from envoy_diff.patcher import PatchResult


class ApplyError(Exception):
    """Raised when a patch cannot be applied cleanly."""


def apply_patch(
    target: Dict[str, Optional[str]],
    patch: PatchResult,
    *,
    strict: bool = False,
) -> Dict[str, Optional[str]]:
    """Return a new env mapping with the patch applied.

    Args:
        target: The original target env mapping.
        patch: The patch to apply.
        strict: When True, raise ApplyError if an 'add' action targets a key
            that already exists in the target.

    Returns:
        A new dictionary with additions, updates, and removals applied.
    """
    result: Dict[str, Optional[str]] = dict(target)

    for entry in patch.entries:
        if entry.action == "add":
            if strict and entry.key in result:
                raise ApplyError(
                    f"Key '{entry.key}' already exists in target (strict mode)."
                )
            result[entry.key] = entry.source_value

        elif entry.action == "update":
            result[entry.key] = entry.source_value

        elif entry.action == "remove":
            result.pop(entry.key, None)

        else:
            raise ApplyError(f"Unknown patch action '{entry.action}' for key '{entry.key}'.")

    return result


def render_env(
    mapping: Dict[str, Optional[str]],
    *,
    sort_keys: bool = True,
) -> str:
    """Render an env mapping as a .env file string.

    Args:
        mapping: Key/value pairs to render.
        sort_keys: When True, output keys in alphabetical order.

    Returns:
        A string in .env file format.
    """
    keys = sorted(mapping.keys()) if sort_keys else list(mapping.keys())
    lines = []
    for key in keys:
        value = mapping[key]
        lines.append(f"{key}={value}" if value is not None else f"{key}=")
    return "\n".join(lines) + ("\n" if lines else "")
