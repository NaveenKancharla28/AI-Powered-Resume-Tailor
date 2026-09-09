"""Deterministic resume diffing for explainable tailoring."""
from __future__ import annotations

import difflib
import re


def _normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip().lower())


def build_resume_diff(original: str, tailored: str) -> list[dict[str, str]]:
    """Return added, removed, and unchanged resume lines."""
    original_lines = original.splitlines()
    tailored_lines = tailored.splitlines()
    matcher = difflib.SequenceMatcher(
        a=[_normalize_line(line) for line in original_lines],
        b=[_normalize_line(line) for line in tailored_lines],
    )
    changes = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        for line in original_lines[i1:i2]:
            changes.append({"type": "removed", "text": line})
        for line in tailored_lines[j1:j2]:
            changes.append({"type": "added", "text": line})
    return changes


def summarize_changes(original: str, tailored: str) -> dict[str, int]:
    changes = build_resume_diff(original, tailored)
    return {
        "added": sum(change["type"] == "added" for change in changes),
        "removed": sum(change["type"] == "removed" for change in changes),
        "total": len(changes),
    }
