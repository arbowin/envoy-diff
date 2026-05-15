"""Format DigestComparison results as text, JSON, or Markdown."""
from __future__ import annotations

import json
from typing import List

from envoy_diff.digester import DigestComparison


def _text_lines(cmp: DigestComparison) -> List[str]:
    lines: List[str] = []
    status = "MATCH" if cmp.match else "MISMATCH"
    lines.append(f"Digest comparison: {status}")
    lines.append(f"  source : {cmp.source.path}")
    lines.append(f"    keys : {cmp.source.key_count}")
    lines.append(f"    hash : {cmp.source.digest}")
    lines.append(f"  target : {cmp.target.path}")
    lines.append(f"    keys : {cmp.target.key_count}")
    lines.append(f"    hash : {cmp.target.digest}")
    if cmp.match:
        lines.append("Files are identical (digest match).")
    else:
        lines.append("Files differ (digest mismatch).")
    return lines


def format_digest_text(cmp: DigestComparison) -> str:
    return "\n".join(_text_lines(cmp))


def format_digest_json(cmp: DigestComparison) -> str:
    payload = {
        "match": cmp.match,
        "source": cmp.source.as_dict(),
        "target": cmp.target.as_dict(),
    }
    return json.dumps(payload, indent=2)


def format_digest_markdown(cmp: DigestComparison) -> str:
    status = "✅ MATCH" if cmp.match else "❌ MISMATCH"
    lines: List[str] = [
        f"## Digest Comparison — {status}",
        "",
        "| Field  | Source | Target |",
        "|--------|--------|--------|",
        f"| Path   | `{cmp.source.path}` | `{cmp.target.path}` |",
        f"| Keys   | {cmp.source.key_count} | {cmp.target.key_count} |",
        f"| Digest | `{cmp.source.digest[:16]}…` | `{cmp.target.digest[:16]}…` |",
    ]
    return "\n".join(lines)


def render_digest(cmp: DigestComparison, fmt: str = "text") -> str:
    """Render *cmp* in the requested *fmt* (text/json/markdown)."""
    fmt = fmt.lower()
    if fmt == "json":
        return format_digest_json(cmp)
    if fmt in {"md", "markdown"}:
        return format_digest_markdown(cmp)
    return format_digest_text(cmp)
